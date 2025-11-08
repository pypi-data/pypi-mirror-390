"""This module provides a function to discover SQLAlchemy and SQLModel models."""
import importlib
from inspect import isclass
from types import ModuleType
from typing import List

from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel

from .utils import get_features_packages


def get_sql_models(features_module: ModuleType) -> List[str]:
    """Discovers SQLAlchemy and DeclarativeBase-mapped model classes within a package.

    Args:
        features_module: The `features` module to search for models in.

    Returns:
        A list of strings representing fully qualified names (module + class name) for all discovered model classes.
    """

    models = set()
    models_modules = get_features_packages(
        features_module=features_module,
        package_name='models.[^\.]*',
        modules_only=True,
    )
    if len(models_modules) == 0:
        print(f"No models modules found in features: {features_module.__name__}")
        return models

    for model_name in models_modules:
        try:
            model_module = importlib.import_module(model_name)
            for attribute_name in dir(model_module):
                model_class = getattr(model_module, attribute_name, None)
                if isclass(model_class) and (
                        issubclass(model_class, SQLModel) or issubclass(model_class, DeclarativeBase)):
                    if hasattr(model_class, '__tablename__'):
                        # print(model_class.__tablename__)
                        models.add(model_name)

        except (ImportError, AttributeError) as e:
            print(f"Could not load model from module '{model_module}' in package '{features_module.__name__}': {e}")
            continue

    models = list(models)

    return models
