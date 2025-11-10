"""
Parameter mapping utilities for PLANQK runtime system.

This module provides functions to map input files to function parameters,
including support for DataPool parameter injection.
"""
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from inspect import Signature, Parameter
from pathlib import Path, PurePath
from typing import Any, Dict, List, Type, get_origin, get_args, Union, Optional
from uuid import UUID

from loguru import logger
from pydantic import BaseModel

from planqk.commons.datapool import DataPool
from planqk.commons.secret import SecretValue


# Type conversion architecture using Strategy pattern
class TypeConverter(ABC):
    """Abstract base class for type-specific converters."""

    @abstractmethod
    def can_handle(self, parameter_type: Type) -> bool:
        """Check if this converter can handle the given type."""
        pass

    @abstractmethod
    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        """Convert string data to the specified type."""
        pass


class UnionTypeConverter(TypeConverter):
    """Handles Union[X, Y] and Optional[T] types."""

    def can_handle(self, parameter_type: Type) -> bool:
        return get_origin(parameter_type) is Union

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        args = get_args(parameter_type)

        if self._is_optional(parameter_type):
            # Optional[T] -> try T, fallback to None
            non_none_type = next(arg for arg in args if arg is not type(None))
            try:
                return registry.convert(data, non_none_type)
            except (ValueError, TypeError, json.JSONDecodeError):
                return None
        else:
            # Union[X, Y] -> try each type in order
            for arg in args:
                try:
                    return registry.convert(data, arg)
                except (ValueError, TypeError, json.JSONDecodeError):
                    continue
            raise ValueError(f"Could not convert data to any type in Union {args}")

    def _is_optional(self, parameter_type: Type) -> bool:
        """Check if type is Optional (Union[T, None])."""
        args = get_args(parameter_type)
        return len(args) == 2 and type(None) in args


class ListTypeConverter(TypeConverter):
    """Handles List[T] and list types."""

    def can_handle(self, parameter_type: Type) -> bool:
        return get_origin(parameter_type) is list

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        json_data = self._parse_json_list(data, parameter_type)
        args = get_args(parameter_type)

        if args:  # List[T] - convert each item to T
            return self._convert_typed_list(json_data, args[0], registry)
        else:  # Plain list - return as-is
            return json_data

    def _parse_json_list(self, data: str, parameter_type: Type) -> list:
        """Parse JSON data and validate it's a list."""
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for list type {parameter_type}: {e}")

        if not isinstance(json_data, list):
            raise ValueError(f"Expected list data for type {parameter_type}, got {type(json_data).__name__}")

        return json_data

    def _convert_typed_list(self, json_data: list, inner_type: Type, registry: 'ConverterRegistry') -> list:
        """Convert each item in list to the specified inner type."""
        converted_items = []
        for i, item in enumerate(json_data):
            try:
                item_data = item if isinstance(item, str) else json.dumps(item)
                converted_item = registry.convert(item_data, inner_type)
                converted_items.append(converted_item)
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                raise ValueError(f"Failed to convert item {i} in list to type {inner_type}: {e}")
        return converted_items


class PrimitiveTypeConverter(TypeConverter):
    """Handles primitive types: str, int, float, bool."""

    def can_handle(self, parameter_type: Type) -> bool:
        return (isinstance(parameter_type, type) and
                issubclass(parameter_type, (str, int, float, bool)))

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        if issubclass(parameter_type, str):
            return data
        elif issubclass(parameter_type, bool):
            return bool(data)
        elif issubclass(parameter_type, int):
            return int(data)
        elif issubclass(parameter_type, float):
            return float(data)


class BaseModelConverter(TypeConverter):
    """Handles Pydantic BaseModel types."""

    def can_handle(self, parameter_type: Type) -> bool:
        try:
            return isinstance(parameter_type, type) and issubclass(parameter_type, BaseModel)
        except TypeError:
            return False

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        return parameter_type.model_validate_json(data)


class TypedDictConverter(TypeConverter):
    """Handles typed Dict[K, V] where values need conversion."""

    def can_handle(self, parameter_type: Type) -> bool:
        origin = get_origin(parameter_type)
        return origin is dict

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for dict type {parameter_type}: {e}")

        if not isinstance(json_data, dict):
            raise ValueError(f"Expected dict data for type {parameter_type}, got {type(json_data).__name__}")

        args = get_args(parameter_type)
        if len(args) >= 2:  # Dict[K, V] - convert values to V
            key_type, value_type = args[0], args[1]
            converted_dict = {}
            for key, value in json_data.items():
                try:
                    # Convert key if needed (usually str, but could be other types)
                    converted_key = key if key_type is str else registry.convert(str(key), key_type)
                    # Convert value to target type
                    value_data = value if isinstance(value, str) else json.dumps(value)
                    converted_value = registry.convert(value_data, value_type)
                    converted_dict[converted_key] = converted_value
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    raise ValueError(f"Failed to convert dict item '{key}' to type {value_type}: {e}")
            return converted_dict
        else:
            # Plain dict or Dict without type args
            return json_data


class TupleTypeConverter(TypeConverter):
    """Handles Tuple[T1, T2, ...] and tuple types."""

    def can_handle(self, parameter_type: Type) -> bool:
        return get_origin(parameter_type) is tuple

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for tuple type {parameter_type}: {e}")

        if not isinstance(json_data, list):
            raise ValueError(f"Expected list data for tuple type {parameter_type}, got {type(json_data).__name__}")

        args = get_args(parameter_type)
        if not args:  # Plain tuple
            return tuple(json_data)

        if len(args) == 2 and args[1] is Ellipsis:  # Tuple[T, ...]
            element_type = args[0]
            converted_items = []
            for i, item in enumerate(json_data):
                try:
                    item_data = item if isinstance(item, str) else json.dumps(item)
                    converted_item = registry.convert(item_data, element_type)
                    converted_items.append(converted_item)
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    raise ValueError(f"Failed to convert tuple item {i} to type {element_type}: {e}")
            return tuple(converted_items)
        else:  # Tuple[T1, T2, T3]
            if len(json_data) != len(args):
                raise ValueError(f"Tuple length mismatch: expected {len(args)} items, got {len(json_data)}")

            converted_items = []
            for i, (item, expected_type) in enumerate(zip(json_data, args)):
                try:
                    item_data = item if isinstance(item, str) else json.dumps(item)
                    converted_item = registry.convert(item_data, expected_type)
                    converted_items.append(converted_item)
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    raise ValueError(f"Failed to convert tuple item {i} to type {expected_type}: {e}")
            return tuple(converted_items)


class SetTypeConverter(TypeConverter):
    """Handles Set[T], FrozenSet[T], set, and frozenset types."""

    def can_handle(self, parameter_type: Type) -> bool:
        origin = get_origin(parameter_type)
        return (origin in (set, frozenset) or
                (isinstance(parameter_type, type) and
                 issubclass(parameter_type, (set, frozenset))))

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for set type {parameter_type}: {e}")

        if not isinstance(json_data, list):
            raise ValueError(f"Expected list data for set type {parameter_type}, got {type(json_data).__name__}")

        origin = get_origin(parameter_type)
        args = get_args(parameter_type)

        if args:  # Set[T] or FrozenSet[T]
            element_type = args[0]
            converted_items = []
            for i, item in enumerate(json_data):
                try:
                    item_data = item if isinstance(item, str) else json.dumps(item)
                    converted_item = registry.convert(item_data, element_type)
                    converted_items.append(converted_item)
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    raise ValueError(f"Failed to convert set item {i} to type {element_type}: {e}")

            if origin is frozenset or parameter_type is frozenset:
                return frozenset(converted_items)
            else:
                return set(converted_items)
        else:  # Plain set or frozenset
            if parameter_type is frozenset:
                return frozenset(json_data)
            else:
                return set(json_data)


class EnumTypeConverter(TypeConverter):
    """Handles Enum types."""

    def can_handle(self, parameter_type: Type) -> bool:
        try:
            return isinstance(parameter_type, type) and issubclass(parameter_type, Enum)
        except TypeError:
            return False

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            # Try to parse as JSON first (for quoted strings or numbers)
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                # If not valid JSON, use the string directly
                json_data = data

            # Try to create enum from value
            return parameter_type(json_data)
        except ValueError as e:
            # If direct value creation fails, try by name
            try:
                return parameter_type[str(json_data)]
            except (KeyError, ValueError):
                valid_values = [e.value for e in parameter_type]
                valid_names = [e.name for e in parameter_type]
                raise ValueError(
                    f"Invalid enum value '{json_data}' for {parameter_type.__name__}. "
                    f"Valid values: {valid_values}, valid names: {valid_names}"
                )


class DateTimeConverter(TypeConverter):
    """Handles datetime, date, and time types."""

    def can_handle(self, parameter_type: Type) -> bool:
        return parameter_type in (datetime, date, time)

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            # Parse as JSON string first
            try:
                json_data = json.loads(data)
                if not isinstance(json_data, str):
                    raise ValueError(f"Expected string for {parameter_type.__name__}, got {type(json_data).__name__}")
                data = json_data
            except json.JSONDecodeError:
                # Use the string directly if not valid JSON
                pass

            if parameter_type is datetime:
                # Try ISO format first, then common formats
                try:
                    return datetime.fromisoformat(data.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        return datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S')
            elif parameter_type is date:
                try:
                    return date.fromisoformat(data)
                except ValueError:
                    return datetime.strptime(data, '%Y-%m-%d').date()
            elif parameter_type is time:
                try:
                    return time.fromisoformat(data)
                except ValueError:
                    return datetime.strptime(data, '%H:%M:%S').time()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid {parameter_type.__name__} format '{data}': {e}")


class UuidConverter(TypeConverter):
    """Handles UUID types."""

    def can_handle(self, parameter_type: Type) -> bool:
        return parameter_type is UUID

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            # Parse as JSON string first
            try:
                json_data = json.loads(data)
                if not isinstance(json_data, str):
                    raise ValueError(f"Expected string for UUID, got {type(json_data).__name__}")
                data = json_data
            except json.JSONDecodeError:
                # Use the string directly if not valid JSON
                pass

            return UUID(data)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format '{data}': {e}")


class DecimalConverter(TypeConverter):
    """Handles Decimal types for precise arithmetic."""

    def can_handle(self, parameter_type: Type) -> bool:
        return parameter_type is Decimal

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            # Parse as JSON number or string
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                # Use the string directly if not valid JSON
                json_data = data

            return Decimal(str(json_data))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Decimal format '{data}': {e}")


class PathConverter(TypeConverter):
    """Handles Path and PurePath types."""

    def can_handle(self, parameter_type: Type) -> bool:
        try:
            return isinstance(parameter_type, type) and issubclass(parameter_type, (Path, PurePath))
        except TypeError:
            return False

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            # Parse as JSON string first
            try:
                json_data = json.loads(data)
                if not isinstance(json_data, str):
                    raise ValueError(f"Expected string for {parameter_type.__name__}, got {type(json_data).__name__}")
                data = json_data
            except json.JSONDecodeError:
                # Use the string directly if not valid JSON
                pass

            return parameter_type(data)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid {parameter_type.__name__} format '{data}': {e}")


class AnyTypeConverter(TypeConverter):
    """Handles typing.Any - returns JSON-parsed data as-is."""

    def can_handle(self, parameter_type: Type) -> bool:
        return parameter_type is Any

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            # If not valid JSON, return the string as-is
            return data


class DefaultTypeConverter(TypeConverter):
    """Handles basic list and dict types without type arguments."""

    def can_handle(self, parameter_type: Type) -> bool:
        return (isinstance(parameter_type, type) and
                issubclass(parameter_type, (list, dict)))

    def convert(self, data: str, parameter_type: Type, registry: 'ConverterRegistry') -> Any:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for type {parameter_type}: {e}")


class ConverterRegistry:
    """Registry for type converters using Strategy pattern."""

    def __init__(self):
        """Initialize registry with default converters in priority order."""
        self.converters: List[TypeConverter] = [
            UnionTypeConverter(),  # Handle Union[X, Y], Optional[T] first
            TupleTypeConverter(),  # Handle Tuple[T1, T2]
            SetTypeConverter(),  # Handle Set[T], frozenset
            TypedDictConverter(),  # Handle Dict[K, V] (both typed and plain)
            ListTypeConverter(),  # Handle List[T]
            EnumTypeConverter(),  # Handle Enum types
            DateTimeConverter(),  # Handle datetime, date, time
            UuidConverter(),  # Handle UUID
            DecimalConverter(),  # Handle Decimal
            PathConverter(),  # Handle Path types
            AnyTypeConverter(),  # Handle typing.Any
            PrimitiveTypeConverter(),  # Handle str, int, float, bool
            BaseModelConverter(),  # Handle Pydantic models
            DefaultTypeConverter(),  # Handle plain list, dict without type args
        ]

    def convert(self, data: str, parameter_type: Type) -> Any:
        """Convert data using the first matching converter."""
        for converter in self.converters:
            if converter.can_handle(parameter_type):
                return converter.convert(data, parameter_type, self)
        raise ValueError(f"Type {parameter_type} is not supported")


# Global converter registry instance
_converter_registry = ConverterRegistry()


def files_to_parameters(input_files: Dict[str, str], signature: Signature) -> Dict[str, Any]:
    """
    Maps input files to parameters of a function signature. If a parameter is not found in the input files,
    the default value of the parameter is used. If the parameter is optional and has no default value,
    it is set to None.

    DataPool parameters are automatically injected based on parameter name and type annotation.

    :param input_files: The input files to be mapped to the parameters.
                        The keys are the parameter names. The values are the file paths.
    :param signature: The signature of the function to which the input files should be mapped.
    :return: A dictionary containing the parameters of the function with input files mapped to them.
    """
    parameters = {}

    logger.debug(f"Found input files: {list(input_files.keys())}")
    logger.debug(f"Parameters in signature: {list(signature.parameters.keys())}")

    for parameter in signature.parameters.values():
        parameter_name = parameter.name
        parameter_type = parameter.annotation

        # Check if parameter is DataPool type
        if is_datapool_type(parameter_type):
            try:
                datapool_instance = create_datapool_instance(parameter_name)
                parameters[parameter_name] = datapool_instance
            except (FileNotFoundError, NotADirectoryError) as e:
                logger.warning(
                    f"DataPool directory not found for parameter '{parameter_name}': {e}"
                )
                if is_optional_type(parameter_type):
                    parameters[parameter_name] = None
                else:
                    # For required DataPool parameters, we might want to fail fast
                    raise
            continue

        # Check if parameter is SecretValue type
        if is_secret_type(parameter_type):
            try:
                secret_instance = create_secret_instance(parameter_name)
                parameters[parameter_name] = secret_instance
            except KeyError as e:
                logger.warning(f"Environment variable not found for secret parameter '{parameter_name}': {e}")
                if is_optional_type(parameter_type):
                    parameters[parameter_name] = None
                else:
                    # For required SecretValue parameters, fail fast
                    raise ValueError(
                        f"Required secret parameter '{parameter_name}' not found. Expected environment variable: {parameter_name_to_env_var(parameter_name)}"
                    ) from e
            continue

        if parameter_name not in input_files:
            try:
                parameters[parameter_name] = map_default(parameter)
            except TypeError:
                pass
            continue

        parameters[parameter_name] = map_input_file(input_files[parameter_name], parameter)

    return parameters


def map_input_file(input_file: str, parameter: Parameter) -> Any:
    """
    Maps an input file to a parameter of a function signature.

    :param input_file: The path to the input file.
    :param parameter: The parameter to which the input file should be mapped.
    :return: The value of the input file as the type of the parameter.
    """
    parameter_type = parameter.annotation

    with open(input_file, "r", encoding="utf-8") as file:
        file_content = file.read()

    return str_to_parameter_type(file_content, parameter_type)


def map_default(parameter: Parameter) -> Any:
    """
    Maps the default value of a parameter to the parameter type.

    :param parameter: The parameter for which the default value should be mapped.
    :return: The default value of the parameter.
    """
    parameter_type = parameter.annotation

    # use default value if available
    if parameter.default != parameter.empty:
        return parameter.default

    # if optional w/o default, set to None
    if is_optional_type(parameter_type):
        return None

    # if it is a Pydantic model, try to create an empty instance (using defaults if available)
    if issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json("{}")

    raise TypeError(f"Could not find a default value for parameter '{parameter.name}' of type '{parameter_type}'")


def str_to_parameter_type(data: str, parameter_type: Any) -> Any:
    """
    Converts a string to a parameter type using registered type converters.
    
    This function uses a Strategy pattern with type-specific converters for
    improved maintainability and extensibility.

    :param data: The string to be converted.
    :param parameter_type: The type to which the string should be converted.
    :return: The value of the string as the type of the parameter.
    """
    return _converter_registry.convert(data, parameter_type)


def is_simple_type(value: Any) -> bool:
    """
    Checks if the value is a simple type (str, int, float, bool).
    """
    return isinstance(value, (str, int, float, bool))


def is_container_type(value: Any) -> bool:
    """
    Checks if the value is a container type (list, tuple, Union, Optional).
    """
    return value is list or value is tuple or value is Union or value is Optional


def is_optional_type(value: Any) -> bool:
    """
    Checks if the value is an optional type (Union with None or Optional).
    """
    origin = get_origin(value)
    if origin is Union:
        args = get_args(value)
        return len(args) == 2 and type(None) in args
    return origin is Optional


def is_datapool_type(parameter_type: Any) -> bool:
    """
    Check if parameter type is DataPool or Optional[DataPool].

    :param parameter_type: The parameter type annotation to check
    :return: True if the parameter type is DataPool or Optional[DataPool], False otherwise
    """
    # Handle Optional[DataPool] case
    origin = get_origin(parameter_type)
    if origin is Union:
        args = get_args(parameter_type)
        return any(arg is DataPool for arg in args if arg is not type(None))

    return parameter_type is DataPool


def create_datapool_instance(parameter_name: str) -> DataPool:
    """
    Create DataPool instance for parameter based on parameter name.

    Creates a DataPool instance pointing to '/var/runtime/datapool/{parameter_name}'.

    :param parameter_name: The name of the parameter, used as the datapool directory name
    :return: DataPool instance for the specified parameter
    :raises FileNotFoundError: If the datapool directory doesn't exist
    :raises NotADirectoryError: If the datapool path exists but is not a directory
    """
    # Import here to get the current value, allowing tests to mock it
    from planqk.commons.constants import DEFAULT_DATAPOOL_DIRECTORY, SECRET_ENV_VAR_PREFIX

    datapool_path = os.path.join(DEFAULT_DATAPOOL_DIRECTORY, parameter_name)
    return DataPool(datapool_path)


def parameter_name_to_env_var(parameter_name: str) -> str:
    """
    Convert parameter name to environment variable format.

    Handles both snake_case and camelCase parameter names:
    - snake_case: iqm_token → SECRET_IQM_TOKEN
    - camelCase: ibmToken → SECRET_IBM_TOKEN
    - UPPER_CASE: API_KEY → SECRET_API_KEY

    :param parameter_name: The parameter name from function signature
    :return: Environment variable name in format SECRET_{UPPER_SNAKE_CASE}
    """
    import re

    # Import constant here to avoid circular dependency
    from planqk.commons.constants import SECRET_ENV_VAR_PREFIX

    # If already in UPPER_CASE with underscores, just prepend SECRET_
    if parameter_name.isupper() or (parameter_name.upper() == parameter_name and '_' in parameter_name):
        return f"{SECRET_ENV_VAR_PREFIX}{parameter_name}"

    # Convert camelCase to snake_case
    # Insert underscore before uppercase letters, then convert to uppercase
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', parameter_name)

    # Convert to uppercase and prepend SECRET_
    return f"{SECRET_ENV_VAR_PREFIX}{snake_case.upper()}"


def is_secret_type(parameter_type: Any) -> bool:
    """
    Check if parameter type is SecretValue or Optional[SecretValue].

    :param parameter_type: The parameter type annotation to check
    :return: True if the parameter type is SecretValue or Optional[SecretValue], False otherwise
    """
    from planqk.commons.secret import SecretValue

    # Handle Optional[SecretValue] case
    origin = get_origin(parameter_type)
    if origin is Union:
        args = get_args(parameter_type)
        return any(arg is SecretValue for arg in args if arg is not type(None))

    return parameter_type is SecretValue


def create_secret_instance(parameter_name: str) -> SecretValue:
    """
    Create SecretValue instance for parameter from environment variable.

    Reads the secret value from environment variable following the naming pattern:
    - parameter_name 'ibmToken' → environment variable 'SECRET_IBM_TOKEN'
    - parameter_name 'iqm_token' → environment variable 'SECRET_IQM_TOKEN'

    :param parameter_name: The name of the parameter, used to derive env var name
    :return: SecretValue instance with the secret value from environment
    :raises KeyError: If the environment variable doesn't exist
    """
    from planqk.commons.secret import SecretValue

    env_var_name = parameter_name_to_env_var(parameter_name)

    if env_var_name not in os.environ:
        raise KeyError(
            f"Environment variable '{env_var_name}' not found for parameter '{parameter_name}'"
        )

    secret_value = os.environ[env_var_name]
    return SecretValue(value=secret_value)
