"""SPIRAL: Self-Play Reinforcement Learning Framework.

Unified package supporting both OAT and Tinker backends.
"""

__version__ = "0.2.0"

# Core components available at top level
from spiral import core, oat, tinker

__all__ = ["core", "oat", "tinker", "__version__"]
