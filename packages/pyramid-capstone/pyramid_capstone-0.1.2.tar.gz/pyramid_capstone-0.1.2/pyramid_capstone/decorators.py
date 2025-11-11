"""
Type-hinted API decorators for Pyramid using venusian pattern.

This module provides FastAPI-like decorators that automatically handle
validation and serialization using Marshmallow schemas and Cornice services.
"""

from typing import Any, Callable, Optional

import venusian


class CapstoneAPI:
    """
    Main decorator class that provides FastAPI-like HTTP method decorators.

    Usage:
        @api.get('/users/{user_id}')
        def get_user(request, user_id: int) -> UserResponse:
            return UserResponse(id=user_id, name="John")
    """

    def __init__(self) -> None:
        self.venusian = venusian

    def get(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for GET requests."""
        return self._create_decorator("GET", path, permission=permission, **kwargs)

    def post(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for POST requests."""
        return self._create_decorator("POST", path, permission=permission, **kwargs)

    def put(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for PUT requests."""
        return self._create_decorator("PUT", path, permission=permission, **kwargs)

    def patch(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for PATCH requests."""
        return self._create_decorator("PATCH", path, permission=permission, **kwargs)

    def delete(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for DELETE requests."""
        return self._create_decorator("DELETE", path, permission=permission, **kwargs)

    def options(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for OPTIONS requests."""
        return self._create_decorator("OPTIONS", path, permission=permission, **kwargs)

    def head(self, path: str, permission: Optional[str] = None, **kwargs: Any) -> Callable:
        """Decorator for HEAD requests."""
        return self._create_decorator("HEAD", path, permission=permission, **kwargs)

    def _create_decorator(self, method: str, path: str, **kwargs: Any) -> Callable:
        """
        Create a decorator for the specified HTTP method and path.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path pattern
            **kwargs: Additional configuration options

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            # Store metadata on the function for later processing
            func.__api_method__ = method
            func.__api_path__ = path
            func.__api_kwargs__ = kwargs

            # Use venusian to register this function for later configuration
            def callback(scanner: Any, name: str, obj: Callable) -> None:
                """Venusian callback to register the view with Pyramid."""
                from .service_builder import register_type_hinted_view

                register_type_hinted_view(scanner.config, obj, method, path, **kwargs)

            # Attach venusian callback with our custom category
            self.venusian.attach(func, callback, category="pyramid_type_hinted", depth=1)

            return func

        return decorator


# Create the main instance that users will import
api = CapstoneAPI()
