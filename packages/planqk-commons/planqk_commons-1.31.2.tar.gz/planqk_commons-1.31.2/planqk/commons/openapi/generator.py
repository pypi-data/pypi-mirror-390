import os
from typing import Dict, Any, Tuple

import yaml

from planqk.commons.constants import ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT, SECRETS_PROPERTY_NAME
from planqk.commons.openapi.schema import generate_parameter_schema, generate_return_schema
from planqk.commons.openapi.template import get_template_managed_service
from planqk.commons.reflection import resolve_signature


class OpenAPIConfig:
    """Configuration object for OpenAPI generation."""

    def __init__(self, entrypoint: str = None, title: str = "PLANQK Service API",
                 version: str = "1", description: str = None):
        self.entrypoint = entrypoint or os.environ.get(ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT)
        self.title = title
        self.version = version
        self.description = description


class OpenAPIGenerator:
    """Generator for OpenAPI specifications from function signatures."""

    def __init__(self, config: OpenAPIConfig):
        self.config = config

    def generate_schemas(self) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], list, list]:
        """Generate parameter and return schemas from function signature."""
        signature = resolve_signature(self.config.entrypoint)

        parameter_schemas, parameter_definitions, required_parameters, secret_parameters = generate_parameter_schema(signature)
        return_schema, return_definitions = generate_return_schema(signature)

        # Combine all schema definitions
        all_definitions = {}
        all_definitions.update(parameter_definitions)
        all_definitions.update(return_definitions)

        return parameter_schemas, return_schema, all_definitions, required_parameters, secret_parameters

    def populate_template(self, parameter_schemas: Dict[str, Any], return_schema: Dict[str, Any],
                          schema_definitions: Dict[str, Any], required_parameters: list,
                          secret_parameters: list) -> Dict[str, Any]:
        """Populate OpenAPI template with generated schemas and configuration."""
        template = get_template_managed_service()

        return populate_openapi_template(
            template, parameter_schemas, return_schema, schema_definitions,
            required_parameters, secret_parameters, self.config.title, self.config.version, self.config.description
        )

    def generate(self) -> Dict[str, Any]:
        """Generate complete OpenAPI specification."""
        parameter_schemas, return_schema, definitions, required_parameters, secret_parameters = self.generate_schemas()
        return self.populate_template(parameter_schemas, return_schema, definitions, required_parameters, secret_parameters)


def generate_openapi(entrypoint: str = os.environ.get(ENTRYPOINT_ENV, DEFAULT_ENTRYPOINT),
                     title: str = "PLANQK Service API",
                     version: str = "1",
                     description: str = None) -> None:
    """
    Generate an OpenAPI specification for a PLANQK Service.

    :param entrypoint: The entrypoint of the service
    :param title: The title of the service, defaults to "PLANQK Service API"
    :param version: The version of the service, defaults to "1"
    :param description: Description to apply to the request body schema
    :return:
    """
    config = OpenAPIConfig(entrypoint, title, version, description)
    generator = OpenAPIGenerator(config)
    openapi = generator.generate()

    print(yaml.dump(openapi, sort_keys=False))


def populate_openapi_template(openapi_template: Dict[str, Any],
                              input_schema: Dict[str, Any],
                              output_schema: Dict[str, Any],
                              schema_definitions: Dict[str, Any],
                              required_parameters: list,
                              secret_parameters: list,
                              title: str,
                              version: str = "1",
                              description: str = None) -> Dict[str, Any]:
    # deep copy of openapi_template
    openapi = dict(openapi_template)

    openapi["components"]["schemas"].update(schema_definitions)

    # start execution route
    if input_schema or secret_parameters:
        request_body_schema = openapi["paths"]["/"]["post"]["requestBody"]["content"]["application/json"]["schema"]

        if input_schema:
            request_body_schema["properties"] = input_schema

            # Add required parameters if any exist
            if required_parameters:
                request_body_schema["required"] = required_parameters

        # Add $secrets object if secret parameters exist
        if secret_parameters:
            if "properties" not in request_body_schema:
                request_body_schema["properties"] = {}

            secrets_schema = {
                "type": "object",
                "description": "Secret values to be injected as environment variables",
                "properties": {},
                "additionalProperties": False  # SECURITY: Prevents injection attacks via unknown properties
            }

            # Add each secret parameter as a string property
            for secret_param in secret_parameters:
                secrets_schema["properties"][secret_param] = {
                    "type": "string",
                    "description": f"Secret value for parameter '{secret_param}'"
                }

            request_body_schema["properties"][SECRETS_PROPERTY_NAME] = secrets_schema

            # Make $secrets required if any secrets exist
            if "required" not in request_body_schema:
                request_body_schema["required"] = []
            request_body_schema["required"].append(SECRETS_PROPERTY_NAME)
    else:
        del openapi["paths"]["/"]["post"]["requestBody"]

    # result route
    if "properties" in output_schema:
        (openapi["paths"]["/{id}/result"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["properties"]
         .update(output_schema["properties"]))

    openapi["info"]["title"] = title
    openapi["info"]["version"] = version

    # Add description to info section if provided
    if description:
        openapi["info"]["description"] = description

    return openapi
