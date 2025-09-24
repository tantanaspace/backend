import magic
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate


class JSONSchemaValidator(BaseValidator):
    """
    Universal class for validating JSON fields using JSON Schema.
    Inherits from Django's BaseValidator for better integration with Django's validation system.
    """

    def __init__(self, schema, message=None, code=None):
        """
        Initialize validator with JSON Schema.

        Args:
            schema (dict): JSON Schema for validation
            message (str, optional): Custom error message
            code (str, optional): Custom error code
        """
        self.schema = schema
        super().__init__(message, code)

    def __call__(self, value):
        """
        Validate value against schema.

        Args:
            value: Value to validate

        Returns:
            value: Validated value

        Raises:
            ValidationError: If value doesn't match schema
        """
        try:
            validate(instance=value, schema=self.schema)
            return value
        except JSONSchemaValidationError as e:
            raise ValidationError(self.message or str(e), code=self.code or "invalid")


def file_validator(max_size_mb=5, allowed_mime_types=None, allowed_extensions=None):
    """
    Returns a generic validator for a FileField or ImageField.

    :param max_size_mb: Maximum allowed file size in megabytes.
    :param allowed_mime_types: List of allowed MIME types.
    :param allowed_extensions: List of allowed extensions (lowercase, no dot).
    """

    def _validator(file):
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(
                _(f"File size must be under {max_size_mb}MB"), code="file_size"
            )

        if allowed_mime_types:
            mime_type = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            if mime_type not in allowed_mime_types:
                raise ValidationError(
                    _(f"Unsupported file type: {mime_type}"), code="mime_type"
                )

        if allowed_extensions:
            ext = file.name.split(".")[-1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"Unsupported file extension: .{ext}", code="extension"
                )

    return _validator
