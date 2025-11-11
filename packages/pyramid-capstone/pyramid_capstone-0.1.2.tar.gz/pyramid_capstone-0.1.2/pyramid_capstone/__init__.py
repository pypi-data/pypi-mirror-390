"""
Pyramid Capstone

A FastAPI-like decorator system for Pyramid that automatically handles
validation and serialization using Marshmallow schemas and Cornice services.

Usage:
    from pyramid_capstone import api
    
    @api.get('/users/{user_id}')
    def get_user(request, user_id: int) -> UserResponse:
        return UserResponse(id=user_id, name="John")
"""

from pycornmarsh import get_spec

from .decorators import api
from .exceptions import (
    ParameterConflictError,
    ParameterMissingError,
    SchemaGenerationError,
    ServiceRegistrationError,
    TypeHintedAPIError,
)

__version__ = "0.0.1"


def capstone_enable_openapi_docs(
    config, title, version, description=None, api_version="v1", api_prefix="/api", security_scheme=None
):
    """
    Enable automatic OpenAPI documentation generation for pyramid-capstone endpoints.
    
    Args:
        config: Pyramid configurator
        title: API title for OpenAPI spec
        version: API version for OpenAPI spec
        description: Optional API description
        api_version: URL version prefix (default: "v1")
        api_prefix: URL prefix for API routes (default: "/api")
        security_scheme: Optional security scheme definition for OpenAPI spec
    
    Example:
        config.capstone_enable_openapi_docs(
            title="My API",
            version="1.0.0",
            description="My amazing API",
            api_version="v1",
            api_prefix="/api",
            security_scheme={
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        )
        
        This will create:
        - /api/v1/openapi.json - OpenAPI specification
        - /api/v1/api-explorer - Swagger UI
    """
    
    def openapi_spec_view(request):
        """Generate OpenAPI specification for pyramid-capstone endpoints."""
        # Ensure the version is in the matchdict for pycornmarsh filtering
        if "version" not in request.matchdict:
            request.matchdict["version"] = api_version
        
        spec = get_spec(
            request=request,
            title=title,
            version=version,
            description=description,
            security_scheme=security_scheme,
        )
        
        # Fix double slashes in paths (pycornmarsh bug workaround)
        if "paths" in spec:
            fixed_paths = {}
            for path, methods in spec["paths"].items():
                # Remove double slashes at the start of paths
                fixed_path = path.replace("//", "/")
                fixed_paths[fixed_path] = methods
            spec["paths"] = fixed_paths
        
        # Ensure server URLs don't have trailing slashes
        if "servers" in spec:
            for server in spec["servers"]:
                if "url" in server and server["url"].endswith("/"):
                    server["url"] = server["url"].rstrip("/")
        
        return spec
    
    # Register the OpenAPI JSON endpoint with {version} placeholder
    route_name = f"capstone_openapi_spec_{api_version}"
    route_path = f"{api_prefix}/{{version}}/openapi.json"
    config.add_route(route_name, route_path)
    config.add_view(openapi_spec_view, route_name=route_name, renderer="json")
    
    # Register the API explorer (Swagger UI)
    config.pyramid_apispec_add_explorer(
        spec_route_name=route_name,
        explorer_route_path=f"{api_prefix}/{{version}}/api-explorer",
    )


def includeme(config):
    """
    Pyramid includeme function for pyramid-capstone.

    This function is called when the library is included via config.include().
    It sets up any necessary configuration for the library.
    """
    # Ensure Cornice is included
    config.include("cornice")

    # Include pycornmarsh for automatic OpenAPI documentation generation
    config.include("pycornmarsh")
    
    # Add the capstone_enable_openapi_docs directive
    config.add_directive("capstone_enable_openapi_docs", capstone_enable_openapi_docs)

    # Add any additional configuration here if needed
    # For now, the library works through venusian scanning, so no additional setup is required


__all__ = [
    "api",
    "TypeHintedAPIError",
    "ParameterConflictError",
    "ParameterMissingError",
    "SchemaGenerationError",
    "ServiceRegistrationError",
    "includeme",
]
