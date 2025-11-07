"""Custom exceptions for the WTF Transcript Converter library."""

from typing import Any, Dict, Optional


class ConversionError(Exception):
    """Raised when a conversion operation fails.

    Attributes:
        message: Error message describing what went wrong
        provider: Name of the provider that caused the error
        original_error: The original exception that caused this error
        context: Additional context information about the error
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.original_error = original_error
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        base_msg = self.message
        if self.provider:
            base_msg = f"[{self.provider}] {base_msg}"
        if self.original_error:
            base_msg = f"{base_msg} (Original: {self.original_error})"
        return base_msg


class ValidationError(Exception):
    """Raised when validation of WTF data fails.

    Attributes:
        message: Error message describing the validation failure
        field: The field that failed validation
        value: The value that failed validation
        errors: List of specific validation errors
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        errors: Optional[list[str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
        self.errors = errors or []

    def __str__(self) -> str:
        """Return string representation of the validation error."""
        base_msg = self.message
        if self.field:
            base_msg = f"Field '{self.field}': {base_msg}"
        if self.errors:
            base_msg = f"{base_msg} Errors: {', '.join(str(e) for e in self.errors)}"
        return base_msg


class ProviderError(Exception):
    """Raised when a provider-specific operation fails.

    Attributes:
        message: Error message describing the provider error
        provider: Name of the provider that caused the error
        operation: The operation that failed
        status_code: HTTP status code if applicable
        response_data: Response data from the provider if applicable
    """

    def __init__(
        self,
        message: str,
        provider: str,
        operation: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.operation = operation
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        """Return string representation of the provider error."""
        base_msg = f"[{self.provider}] {self.message}"
        if self.operation:
            base_msg = f"{base_msg} (Operation: {self.operation})"
        if self.status_code:
            base_msg = f"{base_msg} (Status: {self.status_code})"
        return base_msg


class ConfigurationError(Exception):
    """Raised when there's a configuration issue.

    Attributes:
        message: Error message describing the configuration issue
        setting: The configuration setting that caused the error
        value: The invalid value
    """

    def __init__(
        self, message: str, setting: Optional[str] = None, value: Optional[Any] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.setting = setting
        self.value = value

    def __str__(self) -> str:
        """Return string representation of the configuration error."""
        base_msg = self.message
        if self.setting:
            base_msg = f"Setting '{self.setting}': {base_msg}"
        if self.value is not None:
            base_msg = f"{base_msg} (Value: {self.value})"
        return base_msg


class AudioProcessingError(Exception):
    """Raised when audio processing fails.

    Attributes:
        message: Error message describing the audio processing failure
        file_path: Path to the audio file that caused the error
        format: Audio format that caused the error
        original_error: The original exception that caused this error
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        format: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.file_path = file_path
        self.format = format
        self.original_error = original_error

    def __str__(self) -> str:
        """Return string representation of the audio processing error."""
        base_msg = self.message
        if self.file_path:
            base_msg = f"File '{self.file_path}': {base_msg}"
        if self.format:
            base_msg = f"{base_msg} (Format: {self.format})"
        if self.original_error:
            base_msg = f"{base_msg} (Original: {self.original_error})"
        return base_msg
