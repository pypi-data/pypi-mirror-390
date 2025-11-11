from typing import Any, Dict, List, Optional, Type, Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .authentication import Auth, auth_data_class_to_dependency
from .route import Route

__all__ = ("Router",)


class Router:
    """Collection of routes with shared configuration and authentication.

    Description:
        Groups related routes together with common settings like URL prefix,
        tags, authentication requirements, and dependencies, then creates a
        configured FastAPI APIRouter instance.
    """

    def __init__(
        self,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        authentications: Optional[List[Auth]] = None,
        dependencies: Optional[List[Any]] = None,
        routes: Optional[List[Route]] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        default_response_class: Optional[Type[Any]] = JSONResponse,
        include_in_schema: bool = True,
        deprecated: bool = False,
    ):
        """Initialize a Router instance and create the APIRouter.

        Description:
            Configures a router with shared settings and routes, converting
            authentication requirements into dependencies and creating the
            underlying FastAPI APIRouter.

        Args:
            prefix: URL prefix for all routes in this router (e.g., "/api/v1").
            tags: List of tags for grouping routes in OpenAPI documentation.
            authentications: List of Auth configurations applied to all routes.
            dependencies: Additional FastAPI dependencies for all routes.
            routes: List of Route objects to include in this router.
            responses: Common response definitions for OpenAPI schema.
            default_response_class: Default response class for all routes.
            include_in_schema: If False, excludes all routes from OpenAPI schema.
            deprecated: If True, marks all routes as deprecated in OpenAPI.

        Returns:
            None
        """

        dependencies = dependencies or []
        for authentication in authentications or []:
            dependencies.extend(auth_data_class_to_dependency(authentication))

        self.dependencies = dependencies

        self.prefix = prefix
        self.tags = tags or []
        self.routes = routes or []
        self.responses = responses
        self.default_response_class = default_response_class
        self.include_in_schema = include_in_schema
        self.deprecated = deprecated
        self.router = self._create_router()

    def _create_router(self) -> APIRouter:
        """Create an APIRouter dynamically based on the configuration.

        Description:
            Builds a FastAPI APIRouter with configured settings and registers
            all routes with their individual configurations.

        Args:
            None

        Returns:
            APIRouter: Configured FastAPI router ready to be included in an application.
        """

        router = APIRouter(
            prefix=self.prefix,
            tags=list(self.tags or []),
            dependencies=self.dependencies,
            responses=self.responses,
            default_response_class=self.default_response_class or JSONResponse,
            include_in_schema=self.include_in_schema,
            deprecated=self.deprecated,
        )

        for route in self.routes:
            # Build kwargs dict and only include response_class if it's not None
            kwargs = {
                "path": route.path,
                "endpoint": route.wrapped_handler(),
                "methods": [route.method.value],
                "response_model": route.response_model,
                "status_code": route.status_code,
                "dependencies": route.dependencies,
                "name": route.name,
                "summary": route.summary,
                "description": route.description,
                "tags": list(route.tags or []),
                "response_description": route.response_description,
                "responses": route.responses,
                "deprecated": route.deprecated,
                "operation_id": route.operation_id,
                "include_in_schema": route.include_in_schema,
                "response_model_exclude_unset": route.response_model_exclude_unset,
                "response_model_exclude_defaults": route.response_model_exclude_defaults,
                "response_model_exclude_none": route.response_model_exclude_none,
                "response_model_by_alias": route.response_model_by_alias,
            }
            
            if route.response_class is not None:
                kwargs["response_class"] = route.response_class
            
            router.add_api_route(**kwargs)
        return router

    def get_router(self) -> APIRouter:
        """Return the underlying APIRouter instance.

        Description:
            Retrieves the configured FastAPI APIRouter for inclusion in an
            Application or another router.

        Args:
            None

        Returns:
            APIRouter: The configured FastAPI APIRouter instance.
        """
        return self.router
