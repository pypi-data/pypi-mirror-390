#!/usr/bin/env python3
"""Simple PyAndroid application example.

This example demonstrates how to create a basic Android application
using the PyAndroid library with UI components and event handling.
"""

from pyandroid import AndroidApp, Activity
from pyandroid.ui import LinearLayout, Widget
from pyandroid.utils import Logger


class MainActivity(Activity):
    """Main activity for the simple app."""
    
    def __init__(self):
        super().__init__("MainActivity")
        self.logger = Logger("MainActivity")
        self.counter = 0
        
    def on_start(self):
        """Initialize the UI when activity starts."""
        self.logger.info("MainActivity starting")
        
        # Create main layout
        layout = LinearLayout("main_layout", orientation="vertical")
        layout.set_padding(20, 20, 20, 20)
        
        # Title text
        title = Widget.create_text_view(
            "title_text",
            "PyAndroid Simple App",
            width=300,
            height=50
        )
        title.set_text_color("#2196F3")
        title.set_text_size(20)
        
        # Counter display
        self.counter_text = Widget.create_text_view(
            "counter_text",
            f"Counter: {self.counter}",
            width=300,
            height=40
        )
        self.counter_text.set_text_size(16)
        
        # Increment button
        increment_btn = Widget.create_button(
            "increment_btn",
            "Increment (+)",
            on_click=self.on_increment_click,
            width=200,
            height=50
        )
        increment_btn.set_background_color("#4CAF50")
        
        # Decrement button
        decrement_btn = Widget.create_button(
            "decrement_btn",
            "Decrement (-)",
            on_click=self.on_decrement_click,
            width=200,
            height=50
        )
        decrement_btn.set_background_color("#F44336")
        
        # Reset button
        reset_btn = Widget.create_button(
            "reset_btn",
            "Reset",
            on_click=self.on_reset_click,
            width=200,
            height=50
        )
        reset_btn.set_background_color("#FF9800")
        
        # Input field for custom increment
        self.input_field = Widget.create_edit_text(
            "custom_input",
            hint="Enter custom increment value",
            width=300,
            height=50
        )
        
        # Custom increment button
        custom_btn = Widget.create_button(
            "custom_btn",
            "Custom Increment",
            on_click=self.on_custom_increment_click,
            width=200,
            height=50
        )
        custom_btn.set_background_color("#9C27B0")
        
        # Add all views to layout
        layout.add_view(title)
        layout.add_view(self.counter_text)
        layout.add_view(increment_btn)
        layout.add_view(decrement_btn)
        layout.add_view(reset_btn)
        layout.add_view(self.input_field)
        layout.add_view(custom_btn)
        
        # Add layout to activity
        self.add_view("main_layout", layout)
        
        self.logger.info("UI initialized successfully")
        
    def on_increment_click(self, view):
        """Handle increment button click."""
        self.counter += 1
        self.update_counter_display()
        self.logger.info(f"Counter incremented to {self.counter}")
        
    def on_decrement_click(self, view):
        """Handle decrement button click."""
        self.counter -= 1
        self.update_counter_display()
        self.logger.info(f"Counter decremented to {self.counter}")
        
    def on_reset_click(self, view):
        """Handle reset button click."""
        self.counter = 0
        self.update_counter_display()
        self.logger.info("Counter reset to 0")
        
    def on_custom_increment_click(self, view):
        """Handle custom increment button click."""
        try:
            custom_value = int(self.input_field.get_text())
            self.counter += custom_value
            self.update_counter_display()
            self.input_field.set_text("")  # Clear input
            self.logger.info(f"Counter incremented by {custom_value} to {self.counter}")
        except ValueError:
            self.logger.warning("Invalid input for custom increment")
            
    def update_counter_display(self):
        """Update the counter display text."""
        self.counter_text.set_text(f"Counter: {self.counter}")
        
        # Change color based on counter value
        if self.counter > 0:
            self.counter_text.set_text_color("#4CAF50")  # Green for positive
        elif self.counter < 0:
            self.counter_text.set_text_color("#F44336")  # Red for negative
        else:
            self.counter_text.set_text_color("#000000")  # Black for zero
            
    def on_resume(self):
        """Called when activity resumes."""
        self.logger.info("MainActivity resumed")
        
    def on_pause(self):
        """Called when activity pauses."""
        self.logger.info("MainActivity paused")
        
    def on_stop(self):
        """Called when activity stops."""
        self.logger.info("MainActivity stopped")


def main():
    """Main function to run the application."""
    # Create application
    app = AndroidApp("SimpleCounterApp", "com.example.simplecounter")
    
    # Register main activity
    app.register_activity("main", MainActivity)
    
    # Start main activity
    app.start_activity("main")
    
    # Run application
    print("Starting Simple PyAndroid Counter App...")
    app.run()
    print("Application finished")


if __name__ == "__main__":
    main()
