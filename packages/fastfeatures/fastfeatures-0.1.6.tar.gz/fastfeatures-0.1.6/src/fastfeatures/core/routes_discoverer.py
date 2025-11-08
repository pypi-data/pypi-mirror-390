"""This module provides a function to discover and include FastAPI routes."""
import importlib
from types import ModuleType

from fastapi import FastAPI, APIRouter

from .utils import get_features_packages


def add_features_routes(application: FastAPI, features_module: ModuleType) -> None:
    """Adds routes from the features module.

    Args:
        application: The FastAPI application.
        features_module: The features module from your project.

    Example:
        ```python
          from fastapi import FastAPI
          from fastfeatures import add_features_routes
          from app import features

          app = FastAPI()
          add_features_routes(app, features)
        ```
    """
    routes_modules = get_features_packages(
        features_module=features_module,
        package_name='routes',
        modules_only=True
    )
    if len(routes_modules) == 0:
        print(f"No routes modules found in features: {features_module.__name__}")
        return

    for module_name in routes_modules:
        try:
            router_module = importlib.import_module(module_name)
            for attribute_name in dir(router_module):
                attribute = getattr(router_module, attribute_name)
                if isinstance(attribute, APIRouter):
                    application.include_router(attribute)
                    print(f"Included router from module: {module_name}")

        except (ImportError, AttributeError) as e:
            print(f"Could not load router from module '{module_name}' in package '{features_module.__name__}': {e}")
            continue
