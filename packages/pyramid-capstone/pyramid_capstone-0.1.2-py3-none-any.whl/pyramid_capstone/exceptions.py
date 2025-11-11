"""
Custom exceptions for the type-hinted API system.

This module defines exceptions that can occur during setup and runtime
of the type-hinted API decorators.
"""


class TypeHintedAPIError(Exception):
    """Base exception for all type-hinted API errors."""

    pass


class ParameterConflictError(TypeHintedAPIError):
    """
    Raised when there are conflicting parameter names between different sources.

    This typically occurs during setup when the same parameter name appears
    in multiple places (e.g., both path and query parameters).
    """

    pass


class ParameterMissingError(TypeHintedAPIError):
    """
    Raised when a required parameter is missing from the request.

    This occurs at runtime when a function requires a parameter that
    is not provided in the request.
    """

    pass


class SchemaGenerationError(TypeHintedAPIError):
    """
    Raised when automatic schema generation fails.

    This can occur when type hints are not supported or when there
    are issues converting types to Marshmallow fields.
    """

    pass


class ServiceRegistrationError(TypeHintedAPIError):
    """
    Raised when there are issues registering a Cornice service.

    This typically occurs during setup when the service configuration
    is invalid or conflicts with existing services.
    """

    pass
