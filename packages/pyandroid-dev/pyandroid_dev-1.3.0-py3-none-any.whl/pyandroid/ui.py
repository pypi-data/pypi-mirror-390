"""Android UI components for PyAndroid library.

This module provides classes for building user interfaces
in Android applications with Python.
"""

from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod


class View(ABC):
    """Base class for all UI views.
    
    Represents a basic UI component in Android.
    """
    
    def __init__(self, view_id: str, width: int = 0, height: int = 0):
        """Initialize view.
        
        Args:
            view_id: Unique identifier for the view
            width: View width in pixels
            height: View height in pixels
        """
        self.view_id = view_id
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.visible = True
        self.enabled = True
        self.background_color = "#FFFFFF"
        self.onclick_listener = None
        
    def set_position(self, x: int, y: int):
        """Set view position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y
        
    def set_size(self, width: int, height: int):
        """Set view size.
        
        Args:
            width: View width
            height: View height
        """
        self.width = width
        self.height = height
        
    def set_visibility(self, visible: bool):
        """Set view visibility.
        
        Args:
            visible: Whether view should be visible
        """
        self.visible = visible
        
    def set_enabled(self, enabled: bool):
        """Set view enabled state.
        
        Args:
            enabled: Whether view should be enabled
        """
        self.enabled = enabled
        
    def set_background_color(self, color: str):
        """Set background color.
        
        Args:
            color: Hex color code (e.g. #FF0000)
        """
        self.background_color = color
        
    def set_on_click_listener(self, callback):
        """Set click event listener.
        
        Args:
            callback: Function to call when view is clicked
        """
        self.onclick_listener = callback
        
    def on_click(self):
        """Handle click events."""
        if self.onclick_listener and self.enabled:
            self.onclick_listener(self)
            
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """Render view to dictionary representation.
        
        Returns:
            Dictionary containing view properties
        """
        pass


class TextView(View):
    """Text display view."""
    
    def __init__(self, view_id: str, text: str = "", **kwargs):
        """Initialize TextView.
        
        Args:
            view_id: Unique identifier
            text: Text to display
            **kwargs: Additional view arguments
        """
        super().__init__(view_id, **kwargs)
        self.text = text
        self.text_color = "#000000"
        self.text_size = 14
        self.font_family = "Arial"
        
    def set_text(self, text: str):
        """Set text content.
        
        Args:
            text: Text to display
        """
        self.text = text
        
    def set_text_color(self, color: str):
        """Set text color.
        
        Args:
            color: Hex color code
        """
        self.text_color = color
        
    def set_text_size(self, size: int):
        """Set text size.
        
        Args:
            size: Font size in pixels
        """
        self.text_size = size
        
    def render(self) -> Dict[str, Any]:
        """Render TextView."""
        return {
            "type": "TextView",
            "id": self.view_id,
            "text": self.text,
            "text_color": self.text_color,
            "text_size": self.text_size,
            "font_family": self.font_family,
            "position": {"x": self.x, "y": self.y},
            "size": {"width": self.width, "height": self.height},
            "visible": self.visible,
            "enabled": self.enabled,
            "background_color": self.background_color
        }


class Button(TextView):
    """Button widget for user interaction."""
    
    def __init__(self, view_id: str, text: str = "Button", **kwargs):
        """Initialize Button.
        
        Args:
            view_id: Unique identifier
            text: Button text
            **kwargs: Additional view arguments
        """
        super().__init__(view_id, text, **kwargs)
        self.background_color = "#2196F3"
        self.text_color = "#FFFFFF"
        
    def render(self) -> Dict[str, Any]:
        """Render Button."""
        data = super().render()
        data["type"] = "Button"
        return data


class EditText(View):
    """Text input field."""
    
    def __init__(self, view_id: str, hint: str = "", **kwargs):
        """Initialize EditText.
        
        Args:
            view_id: Unique identifier
            hint: Placeholder text
            **kwargs: Additional view arguments
        """
        super().__init__(view_id, **kwargs)
        self.text = ""
        self.hint = hint
        self.text_color = "#000000"
        self.hint_color = "#808080"
        
    def set_text(self, text: str):
        """Set input text.
        
        Args:
            text: Input text
        """
        self.text = text
        
    def get_text(self) -> str:
        """Get current text.
        
        Returns:
            Current input text
        """
        return self.text
        
    def render(self) -> Dict[str, Any]:
        """Render EditText."""
        return {
            "type": "EditText",
            "id": self.view_id,
            "text": self.text,
            "hint": self.hint,
            "text_color": self.text_color,
            "hint_color": self.hint_color,
            "position": {"x": self.x, "y": self.y},
            "size": {"width": self.width, "height": self.height},
            "visible": self.visible,
            "enabled": self.enabled,
            "background_color": self.background_color
        }


class Layout(ABC):
    """Base class for view containers."""
    
    def __init__(self, layout_id: str):
        """Initialize Layout.
        
        Args:
            layout_id: Unique identifier for layout
        """
        self.layout_id = layout_id
        self.children: List[View] = []
        self.padding = {"left": 0, "top": 0, "right": 0, "bottom": 0}
        
    def add_view(self, view: View):
        """Add child view to layout.
        
        Args:
            view: View to add
        """
        self.children.append(view)
        
    def remove_view(self, view: View):
        """Remove child view from layout.
        
        Args:
            view: View to remove
        """
        if view in self.children:
            self.children.remove(view)
            
    def find_view_by_id(self, view_id: str) -> Optional[View]:
        """Find child view by ID.
        
        Args:
            view_id: View identifier to search for
            
        Returns:
            View instance or None if not found
        """
        for view in self.children:
            if view.view_id == view_id:
                return view
        return None
        
    def set_padding(self, left: int, top: int, right: int, bottom: int):
        """Set layout padding.
        
        Args:
            left: Left padding
            top: Top padding  
            right: Right padding
            bottom: Bottom padding
        """
        self.padding = {
            "left": left, 
            "top": top, 
            "right": right, 
            "bottom": bottom
        }
        
    @abstractmethod
    def arrange_children(self):
        """Arrange child views within the layout."""
        pass
        
    def render(self) -> Dict[str, Any]:
        """Render layout and all children.
        
        Returns:
            Dictionary representation of layout
        """
        self.arrange_children()
        return {
            "type": self.__class__.__name__,
            "id": self.layout_id,
            "padding": self.padding,
            "children": [child.render() for child in self.children]
        }


class LinearLayout(Layout):
    """Linear layout arranges children in a single direction."""
    
    def __init__(self, layout_id: str, orientation: str = "vertical"):
        """Initialize LinearLayout.
        
        Args:
            layout_id: Unique identifier
            orientation: "vertical" or "horizontal"
        """
        super().__init__(layout_id)
        self.orientation = orientation
        
    def arrange_children(self):
        """Arrange children linearly."""
        current_x = self.padding["left"]
        current_y = self.padding["top"]
        
        for child in self.children:
            child.set_position(current_x, current_y)
            
            if self.orientation == "vertical":
                current_y += child.height + 10  # 10px margin
            else:  # horizontal
                current_x += child.width + 10  # 10px margin


class RelativeLayout(Layout):
    """Relative layout allows positioning relative to parent or siblings."""
    
    def __init__(self, layout_id: str):
        """Initialize RelativeLayout.
        
        Args:
            layout_id: Unique identifier
        """
        super().__init__(layout_id)
        
    def arrange_children(self):
        """Arrange children based on relative positioning rules.
        
        For now, this is a basic implementation that doesn't
        move children from their set positions.
        """
        pass  # Children maintain their manually set positions


class Widget:
    """Helper class for creating common UI widgets."""
    
    @staticmethod
    def create_text_view(view_id: str, text: str, **kwargs) -> TextView:
        """Create a TextView widget.
        
        Args:
            view_id: Unique identifier
            text: Text to display
            **kwargs: Additional arguments
            
        Returns:
            TextView instance
        """
        return TextView(view_id, text, **kwargs)
        
    @staticmethod
    def create_button(view_id: str, text: str, on_click=None, **kwargs) -> Button:
        """Create a Button widget.
        
        Args:
            view_id: Unique identifier
            text: Button text
            on_click: Click event handler
            **kwargs: Additional arguments
            
        Returns:
            Button instance
        """
        button = Button(view_id, text, **kwargs)
        if on_click:
            button.set_on_click_listener(on_click)
        return button
        
    @staticmethod
    def create_edit_text(view_id: str, hint: str = "", **kwargs) -> EditText:
        """Create an EditText widget.
        
        Args:
            view_id: Unique identifier
            hint: Placeholder text
            **kwargs: Additional arguments
            
        Returns:
            EditText instance
        """
        return EditText(view_id, hint, **kwargs)
