"""Public entry point for the Glove80 toolkit.

Minimal, obvious surface for common tasks:
 - Discover families via :func:`list_families`.
 - Build a variant via :func:`build_layout`.
 - Apply a feature bundle via :func:`apply_feature`.
 - Grab a batteries-included example via :func:`bilateral_home_row_components`.
"""

from .features import apply_feature, bilateral_home_row_components
from .layouts.family import build_layout, list_families

# Ensure layout families are registered when importing the top-level package.
# The generator module imports each family's `layouts` module, which registers
# itself with the global REGISTRY as a side-effect. Without this import the
# registry would be empty when consumers call `list_families()` or
# `build_layout(...)` directly from the package as documented.
from .layouts import generator as _generator  # noqa: F401

__all__ = [
    "build_layout",
    "list_families",
    "apply_feature",
    "bilateral_home_row_components",
]
