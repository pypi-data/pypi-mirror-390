from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, PrivateAttr, model_serializer


class SecretValue(BaseModel):
    """
    A container for sensitive values that provides:
    - Automatic redaction in string representations
    - Single-use unwrapping with locking mechanism
    - Custom JSON serialization that unwraps the value

    Once unwrapped, the secret is locked and cannot be unwrapped again.

    Example:
        >>> secret = SecretValue(value="my-secret-password")
        >>> print(secret)  # Output: [redacted]
        >>> actual_value = secret.unwrap()  # Returns "my-secret-password"
        >>> secret.unwrap()  # Raises ValueError: Secret is locked
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        # Prevent Pydantic from exposing the value in validation errors
        hide_input_in_errors=True,
    )

    _value: str = PrivateAttr()
    _locked: bool = PrivateAttr(default=False)

    def __init__(self, value: str, **kwargs) -> None:
        """
        Initialize a SecretValue with the given string value.

        Args:
            value: The secret string to protect
        """
        super().__init__(**kwargs)
        self._value = value

    def __str__(self) -> str:
        """
        Return redacted representation for string conversion.

        Returns:
            The string "[redacted]"
        """
        return "[redacted]"

    def __repr__(self) -> str:
        """
        Return redacted representation for repr().

        Returns:
            The string "SecretValue([redacted])"
        """
        return "SecretValue([redacted])"

    @property
    def is_locked(self) -> bool:
        """
        Check if the secret has been locked (unwrapped).

        Returns:
            True if the secret has been unwrapped and is locked, False otherwise
        """
        return self._locked

    def unwrap(self) -> str:
        """
        Unwrap and return the actual secret value.

        This method can only be called once. After the first call, the secret
        is locked and subsequent calls will raise a ValueError.

        Returns:
            The actual secret string value

        Raises:
            ValueError: If the secret has already been unwrapped (is locked)
        """
        if self._locked:
            raise ValueError("Secret is locked and cannot be unwrapped")

        self._locked = True
        return self._value

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """
        Custom serializer for JSON output that exposes the secret value.

        This is called during JSON serialization (e.g., model_dump_json()).

        Note: Unlike unwrap(), serialization does NOT lock the secret and can be
        called multiple times. The secret value is exposed during serialization
        to match the Java implementation behavior.

        Returns:
            Dictionary with 'value' key containing the secret (not redacted)
        """
        return {"value": self._value}
