"""Core Android application components.

This module provides the fundamental classes for building Android applications
with Python, including App, Activity, and Intent management.
"""

import logging
from typing import Dict, Any, Optional, Callable


class AndroidApp:
    """Main Android Application class.
    
    This class represents the main Android application and manages
    the application lifecycle and global state.
    """
    
    def __init__(self, app_name: str, package_name: str, use_gui: bool = True):
        """Initialize Android application.
        
        Args:
            app_name: Human readable application name
            package_name: Android package name (e.g. com.example.myapp)
            use_gui: Whether to use GUI rendering (requires Kivy)
        """
        self.app_name = app_name
        self.package_name = package_name
        self.use_gui = use_gui
        self.activities = {}
        self.current_activity = None
        self.logger = logging.getLogger(f"PyAndroid.{app_name}")
        self.renderer = None
        
        # Initialize renderer if GUI is enabled
        if self.use_gui:
            try:
                from .backend import KivyRenderer
                self.renderer = KivyRenderer(self)
                self.logger.info("Kivy renderer initialized")
            except ImportError:
                self.logger.warning("Kivy not available. Running in console mode.")
                self.use_gui = False
        
    def register_activity(self, activity_name: str, activity_class):
        """Register an activity with the application.
        
        Args:
            activity_name: Name identifier for the activity
            activity_class: Activity class to register
        """
        self.activities[activity_name] = activity_class
        self.logger.info(f"Registered activity: {activity_name}")
        
    def start_activity(self, activity_name: str, **kwargs):
        """Start a specific activity.
        
        Args:
            activity_name: Name of activity to start
            **kwargs: Arguments to pass to activity
        """
        if activity_name in self.activities:
            activity_class = self.activities[activity_name]
            self.current_activity = activity_class(**kwargs)
            self.current_activity.start()
            self.logger.info(f"Started activity: {activity_name}")
        else:
            raise ValueError(f"Activity {activity_name} not registered")
            
    def run(self):
        """Run the Android application."""
        self.logger.info(f"Starting {self.app_name} application")
        if self.current_activity:
            self.current_activity.resume()
            
            # If GUI is enabled, start Kivy rendering
            if self.use_gui and self.renderer:
                self.logger.info("Starting GUI mode with Kivy")
                self.renderer.run()
            else:
                self.logger.info("Running in console mode (no GUI)")


class Activity:
    """Android Activity base class.
    
    Represents a single screen in an Android application.
    """
    
    def __init__(self, name: str):
        """Initialize activity.
        
        Args:
            name: Activity name identifier
        """
        self.name = name
        self.state = "created"
        self.views = {}
        self.logger = logging.getLogger(f"PyAndroid.Activity.{name}")
        
    def start(self):
        """Start the activity."""
        self.state = "started"
        self.on_start()
        self.logger.info(f"Activity {self.name} started")
        
    def resume(self):
        """Resume the activity."""
        self.state = "resumed"
        self.on_resume()
        self.logger.info(f"Activity {self.name} resumed")
        
    def pause(self):
        """Pause the activity."""
        self.state = "paused"
        self.on_pause()
        self.logger.info(f"Activity {self.name} paused")
        
    def stop(self):
        """Stop the activity."""
        self.state = "stopped"
        self.on_stop()
        self.logger.info(f"Activity {self.name} stopped")
        
    def destroy(self):
        """Destroy the activity."""
        self.state = "destroyed"
        self.on_destroy()
        self.logger.info(f"Activity {self.name} destroyed")
        
    def on_start(self):
        """Called when activity starts. Override in subclasses."""
        pass
        
    def on_resume(self):
        """Called when activity resumes. Override in subclasses."""
        pass
        
    def on_pause(self):
        """Called when activity pauses. Override in subclasses."""
        pass
        
    def on_stop(self):
        """Called when activity stops. Override in subclasses."""
        pass
        
    def on_destroy(self):
        """Called when activity is destroyed. Override in subclasses."""
        pass
        
    def add_view(self, view_id: str, view):
        """Add a view to this activity.
        
        Args:
            view_id: Unique identifier for the view
            view: View instance to add
        """
        self.views[view_id] = view
        
    def get_view(self, view_id: str):
        """Get a view by ID.
        
        Args:
            view_id: View identifier
            
        Returns:
            View instance or None if not found
        """
        return self.views.get(view_id)


class Intent:
    """Android Intent for inter-component communication.
    
    Represents an intention to perform an action.
    """
    
    def __init__(self, action: str, target: Optional[str] = None):
        """Initialize intent.
        
        Args:
            action: Action to perform
            target: Target component (optional)
        """
        self.action = action
        self.target = target
        self.extras = {}
        
    def put_extra(self, key: str, value: Any):
        """Add extra data to intent.
        
        Args:
            key: Data key
            value: Data value
        """
        self.extras[key] = value
        
    def get_extra(self, key: str, default: Any = None) -> Any:
        """Get extra data from intent.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Data value or default
        """
        return self.extras.get(key, default)
