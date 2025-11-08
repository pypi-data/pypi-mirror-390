"""This module provides utility functions for the fast-features package."""
import pkgutil
import re
from types import ModuleType
from typing import List


def get_features_packages(features_module: ModuleType, package_name: str, modules_only: bool = True) -> List[str]:
    """Generate a list of packages names from the given 'features' package that match specific criteria.

    Args:
        features_module: The main features package to search within for modules matching certain
        conditions. Must be an actual Python package, not just any object with attributes like `__name__`.
        package_name: Part of the sub-module or package names' pattern that should match in their full path
        from 'features_module'. This is used as a filter to identify relevant child modules for extraction within
        features_packages. It accepts RegEx.
        modules_only: True to return only modules, False to return modules and packages. Defaults to True.

    Returns:
        A list of fully qualified names (including the package name) that match module patterns ending
        with `package_name`, that belongs to the inner 'features' package, and are not part of a sub-package themselves.
        These modules should also include `package_name` as their last component if provided.
    """

    packages = list(
        pkgutil.walk_packages(
            path=features_module.__path__,
            prefix=features_module.__name__ + ".",
        )
    )
    modules_list: List[str] = []
    if len(packages) > 0:
        for _, mod_name, is_pkg in packages:
            # Filter out the sub-packages themselves and only consider non-package child modules.
            # Ensures the last part of mod_name matches the user-specified pattern.
            if is_pkg != modules_only:
                regex = fr"features\.[^\.]*\.{package_name}$"
                match = re.search(regex, mod_name)
                if match:
                    modules_list.append(mod_name)

    return modules_list
