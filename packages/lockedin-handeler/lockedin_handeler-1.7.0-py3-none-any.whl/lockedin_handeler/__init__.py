"""
Convex Space Manager - A simple Python package for managing space availability in Convex.

This package provides an easy-to-use interface for updating space availability
in your Convex database without needing the full Convex project setup.
"""

from .convex_handler import ConvexSpaceManager, convex_sync

__version__ = "1.7.0"
__author__ = "KAO"
__email__ = "kao@overload.studio"

__all__ = ["ConvexSpaceManager", "LicensePlateTracker", "convex_sync"]
