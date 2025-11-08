# app/features/__init__.py

# ---------------------------------------------------------------------------
# AUTOMATED MODEL DISCOVERY (provided by fastfeatures)
# ---------------------------------------------------------------------------
# For larger projects, you may want to automatically discover and import all
# SQLModel classes instead of importing them manually. To enable this,
# comment out the "MANUAL MODEL IMPORTS" section below and uncomment this
# section.
#
# from fastfeatures import get_sql_models
# import sys
#
# # Get a reference to the 'features' package module itself.
# features_package = sys.modules[__name__]
#
# # Pass the module object to the discovery function
# __all__ = get_sql_models(features_package)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# MANUAL MODEL IMPORTS (Recommended for clarity and IDE support)
# ---------------------------------------------------------------------------
# Explicitly import your models here. This approach is more verbose but
# provides better support for IDEs (e.g., autocompletion, type checking) and
# makes the dependency chain easier to follow for new developers.
#
#
# Add models here as you create them
# from .user.models import User
# from .account.models import Account
# from .another_feature.models import AnotherModel
#
# __all__ = [
#     "User",
#     "Account",
#     "AnotherModel",
# ]
# ---------------------------------------------------------------------------
