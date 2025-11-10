"""Backend rendering engines for PyAndroid.

This module provides different rendering backends for PyAndroid applications.
Currently supports: Kivy
"""

from .kivy_backend import KivyRenderer

__all__ = ['KivyRenderer']
