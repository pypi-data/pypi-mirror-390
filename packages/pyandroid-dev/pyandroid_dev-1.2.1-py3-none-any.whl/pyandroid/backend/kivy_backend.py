"""Kivy backend for PyAndroid rendering.

This module provides a Kivy-based rendering engine that translates
PyAndroid UI components to actual Kivy widgets.
"""

import logging
from typing import Dict, Any, Optional

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button as KivyButton
    from kivy.uix.textinput import TextInput
    from kivy.graphics import Color, Rectangle
    from kivy.core.window import Window
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False
    logging.warning("Kivy not installed. GUI features will not work. Install with: pip install kivy")


class KivyRenderer:
    """Kivy-based renderer for PyAndroid applications."""
    
    def __init__(self, android_app):
        """Initialize Kivy renderer.
        
        Args:
            android_app: AndroidApp instance to render
        """
        if not KIVY_AVAILABLE:
            raise ImportError("Kivy is required for GUI rendering. Install with: pip install kivy")
        
        self.android_app = android_app
        self.widget_map = {}
        self.logger = logging.getLogger("PyAndroid.KivyRenderer")
        
    def hex_to_rgba(self, hex_color: str) -> tuple:
        """Convert hex color to RGBA tuple.
        
        Args:
            hex_color: Hex color string (e.g., #FF0000)
            
        Returns:
            RGBA tuple with values 0-1
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b, 1.0)
        return (1.0, 1.0, 1.0, 1.0)
    
    def render_view(self, view, parent_widget=None):
        """Render a PyAndroid view to Kivy widget.
        
        Args:
            view: PyAndroid view to render
            parent_widget: Parent Kivy widget
            
        Returns:
            Kivy widget representation
        """
        view_data = view.render()
        widget = None
        
        if view_data["type"] == "TextView":
            widget = Label(
                text=view_data["text"],
                size_hint=(None, None),
                size=(view_data["size"]["width"] or 100, view_data["size"]["height"] or 50),
                color=self.hex_to_rgba(view_data["text_color"]),
                font_size=view_data["text_size"]
            )
            # Set background color
            with widget.canvas.before:
                Color(*self.hex_to_rgba(view_data["background_color"]))
                widget.bg_rect = Rectangle(size=widget.size, pos=widget.pos)
            widget.bind(size=self._update_rect, pos=self._update_rect)
            
        elif view_data["type"] == "Button":
            widget = KivyButton(
                text=view_data["text"],
                size_hint=(None, None),
                size=(view_data["size"]["width"] or 100, view_data["size"]["height"] or 50),
                color=self.hex_to_rgba(view_data["text_color"]),
                font_size=view_data["text_size"]
            )
            # Set background color
            widget.background_color = self.hex_to_rgba(view_data["background_color"])
            
            # Bind click event
            if view.onclick_listener:
                widget.bind(on_press=lambda btn: view.on_click())
                
        elif view_data["type"] == "EditText":
            widget = TextInput(
                text=view_data["text"],
                hint_text=view_data["hint"],
                size_hint=(None, None),
                size=(view_data["size"]["width"] or 200, view_data["size"]["height"] or 40),
                foreground_color=self.hex_to_rgba(view_data["text_color"]),
                background_color=self.hex_to_rgba(view_data["background_color"])
            )
        
        if widget:
            self.widget_map[view.view_id] = widget
            if parent_widget:
                parent_widget.add_widget(widget)
                
        return widget
    
    def _update_rect(self, instance, value):
        """Update background rectangle when widget size/position changes."""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def render_layout(self, layout, parent_widget=None):
        """Render a PyAndroid layout to Kivy layout.
        
        Args:
            layout: PyAndroid layout to render
            parent_widget: Parent Kivy widget
            
        Returns:
            Kivy layout widget
        """
        layout_data = layout.render()
        kivy_layout = None
        
        if layout_data["type"] == "LinearLayout":
            orientation = 'vertical' if layout.orientation == 'vertical' else 'horizontal'
            kivy_layout = BoxLayout(
                orientation=orientation,
                padding=[layout_data["padding"]["left"], 
                        layout_data["padding"]["top"],
                        layout_data["padding"]["right"], 
                        layout_data["padding"]["bottom"]],
                spacing=10
            )
            
            # Render child views
            for child in layout.children:
                if hasattr(child, 'children'):  # It's a layout
                    child_widget = self.render_layout(child, kivy_layout)
                else:  # It's a view
                    child_widget = self.render_view(child, kivy_layout)
        
        elif layout_data["type"] == "RelativeLayout":
            kivy_layout = BoxLayout(orientation='vertical')  # Simplified
            for child in layout.children:
                if hasattr(child, 'children'):
                    child_widget = self.render_layout(child, kivy_layout)
                else:
                    child_widget = self.render_view(child, kivy_layout)
        
        if kivy_layout and parent_widget:
            parent_widget.add_widget(kivy_layout)
            
        return kivy_layout
    
    def create_app(self, activity):
        """Create Kivy App from PyAndroid Activity.
        
        Args:
            activity: PyAndroid Activity to render
            
        Returns:
            KivyApp instance
        """
        renderer = self
        
        class PyAndroidKivyApp(App):
            def build(self):
                # Set window title
                Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Dark background
                self.title = renderer.android_app.app_name
                
                # Create main layout
                root = BoxLayout(orientation='vertical')
                
                # Render all views from activity
                for view_id, view in activity.views.items():
                    if hasattr(view, 'children'):  # It's a layout
                        renderer.render_layout(view, root)
                    else:  # It's a view
                        renderer.render_view(view, root)
                
                return root
        
        return PyAndroidKivyApp()
    
    def run(self):
        """Run the Kivy application."""
        if self.android_app.current_activity:
            kivy_app = self.create_app(self.android_app.current_activity)
            kivy_app.run()
        else:
            raise RuntimeError("No activity is currently running")
