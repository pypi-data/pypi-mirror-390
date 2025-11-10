"""PyAndroid - A Python library for creating Android applications.

This library provides a Pythonic interface for building Android applications
with support for GUI rendering through Kivy.

Basic Usage:
    >>> from pyandroid import AndroidApp, Activity
    >>> from pyandroid.ui import LinearLayout, Button
    >>>
    >>> class MainActivity(Activity):
    ...     def on_start(self):
    ...         layout = LinearLayout("main", orientation="vertical")
    ...         button = Button("btn1", "Click Me")
    ...         layout.add_view(button)
    ...         self.add_view("main", layout)
    >>>
    >>> app = AndroidApp("MyApp", "com.example.myapp")
    >>> app.register_activity("main", MainActivity)
    >>> app.start_activity("main")
    >>> app.run()

For more examples, see the examples/ directory in the repository.
"""

from .core import AndroidApp, Activity, Intent
from . import ui
from . import utils
from .__version__ import __version__, __author__, __license__

__all__ = [
    "AndroidApp",
    "Activity",
    "Intent",
    "ui",
    "utils",
    "__version__",
]

# Attribution requirement as per license
print(f"PyAndroid v{__version__} - Built by {__author__}")
print("GitHub: https://github.com/subhobhai943/pyandroid-dev")
