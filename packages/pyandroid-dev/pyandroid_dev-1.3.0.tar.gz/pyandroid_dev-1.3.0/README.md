# PyAndroid - Python Library for Android Development

[![PyPI version](https://badge.fury.io/py/pyandroid.svg)](https://badge.fury.io/py/pyandroid)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyandroid.svg)](https://pypi.org/project/pyandroid/)
[![License](https://img.shields.io/badge/license-Custom-blue.svg)](LICENSE)
[![Tests](https://github.com/subhobhai943/pyandroid-dev/actions/workflows/tests.yml/badge.svg)](https://github.com/subhobhai943/pyandroid-dev/actions/workflows/tests.yml)
[![GitHub Stars](https://img.shields.io/github/stars/subhobhai943/pyandroid-dev.svg)](https://github.com/subhobhai943/pyandroid-dev/stargazers)

A comprehensive Python library for Android application development with **real GUI support**. PyAndroid provides a Pythonic interface for building Android applications using familiar Python patterns, with cross-platform deployment capabilities.

## ✨ Key Features

- 📱 **True Android Development**: Build real Android apps with Python
- 💻 **GUI Support**: Actual graphical interfaces powered by Kivy
- 🎯 **Pythonic API**: Familiar Python syntax and patterns
- 🚀 **Cross-Platform**: Deploy to Desktop, Android, and iOS
- 🧩 **Component-Based**: Activities, Intents, Views, and Layouts
- 📦 **Battery Included**: File management, networking, logging utilities
- 🔧 **Extensible**: Easy to extend with custom components
- ✅ **Well-Tested**: Comprehensive test coverage
- 📚 **Documented**: Full API documentation and examples

## 📥 Installation

### Quick Install

```bash
pip install pyandroid-dev
```

### With GUI Support (Recommended)

```bash
# Install with Kivy for GUI rendering
pip install "pyandroid[gui]"
```

### Development Installation

```bash
# Install with all development tools
pip install "pyandroid[dev,gui]"

# Or install from source
git clone https://github.com/subhobhai943/pyandroid-dev.git
cd pyandroid-dev
pip install -e ".[gui]"
```

## 🚀 Quick Start

### Your First PyAndroid App

```python
from pyandroid import AndroidApp, Activity
from pyandroid.ui import LinearLayout, Button, TextView

class MainActivity(Activity):
    def __init__(self):
        super().__init__("MainActivity")
        self.counter = 0
        
    def on_start(self):
        # Create main layout
        layout = LinearLayout("main_layout", orientation="vertical")
        
        # Add title
        title = TextView("title", "PyAndroid Counter App")
        title.set_text_size(24)
        title.set_text_color("#2196F3")
        layout.add_view(title)
        
        # Add counter display
        self.counter_text = TextView("counter", "Count: 0")
        self.counter_text.set_text_size(32)
        layout.add_view(self.counter_text)
        
        # Add increment button
        button = Button("btn_increment", "Increment")
        button.set_background_color("#4CAF50")
        button.set_on_click_listener(self.increment_counter)
        layout.add_view(button)
        
        # Set layout
        self.add_view("main_layout", layout)
    
    def increment_counter(self, view):
        self.counter += 1
        self.counter_text.set_text(f"Count: {self.counter}")

# Create and run app
app = AndroidApp("Counter App", "com.example.counter")
app.register_activity("main", MainActivity)
app.start_activity("main")
app.run()
```

Run this code and a **real window opens** with a working GUI! 🎉

## 📚 Documentation

### Core Components

#### AndroidApp - Main Application

```python
from pyandroid import AndroidApp

# Create app with GUI support (default)
app = AndroidApp("MyApp", "com.example.myapp")

# Create app without GUI (console mode)
app = AndroidApp("MyApp", "com.example.myapp", use_gui=False)

# Register activities
app.register_activity("main", MainActivity)
app.register_activity("settings", SettingsActivity)

# Start activity
app.start_activity("main")

# Run the app
app.run()
```

#### Activity - Application Screens

```python
from pyandroid import Activity
from pyandroid.ui import LinearLayout, TextView

class MyActivity(Activity):
    def __init__(self):
        super().__init__("MyActivity")
    
    def on_start(self):
        """Called when activity starts"""
        # Setup UI here
        pass
    
    def on_resume(self):
        """Called when activity resumes"""
        pass
    
    def on_pause(self):
        """Called when activity pauses"""
        pass
```

### UI Components

#### TextView - Display Text

```python
from pyandroid.ui import TextView

title = TextView("title", "Welcome!")
title.set_text_color("#FF5722")
title.set_text_size(28)
title.set_background_color("#FFFFFF")
```

#### Button - Interactive Element

```python
from pyandroid.ui import Button

def on_click(view):
    print("Button clicked!")

button = Button("my_button", "Click Me")
button.set_background_color("#2196F3")
button.set_text_color("#FFFFFF")
button.set_on_click_listener(on_click)
```

#### EditText - User Input

```python
from pyandroid.ui import EditText

input_field = EditText("user_input", hint="Enter your name")
input_field.set_text("John")
text = input_field.get_text()
```

#### Layouts - Organize Views

```python
from pyandroid.ui import LinearLayout, TextView, Button

# Vertical layout
layout = LinearLayout("main", orientation="vertical")

# Add children
layout.add_view(TextView("tv1", "Title"))
layout.add_view(Button("btn1", "Action"))

# Horizontal layout
row = LinearLayout("row", orientation="horizontal")
row.add_view(Button("btn2", "Left"))
row.add_view(Button("btn3", "Right"))

layout.add_view(row)
```

### Utilities

#### File Management

```python
from pyandroid.utils import FileManager

fm = FileManager("MyApp")

# JSON files
data = {"user": "Alice", "score": 95}
fm.save_json("data.json", data)
loaded = fm.load_json("data.json")

# Text files
fm.write_file("notes.txt", "My notes")
content = fm.read_file("notes.txt")

# List files
files = fm.list_files()
```

#### Networking

```python
from pyandroid.utils import NetworkManager

net = NetworkManager("MyApp")

# Check connection
if net.is_connected():
    # GET request
    response = net.get("https://api.example.com/data")
    
    # POST with JSON
    data = {"name": "Bob", "age": 25}
    result = net.post_json("https://api.example.com/users", data)
```

#### Logging

```python
from pyandroid.utils import Logger

logger = Logger("MyApp")

logger.debug("Debug information")
logger.info("App started")
logger.warning("Low battery")
logger.error("Connection failed")
```

## 📱 Building APK for Android

Convert your Python app to an Android APK:

### Using Buildozer (Recommended)

```bash
# Install Buildozer
pip install buildozer

# Initialize
buildozer init

# Edit buildozer.spec
# requirements = python3,kivy,pyandroid

# Build APK (first time: 20-60 minutes)
buildozer -v android debug

# Deploy to connected device
buildozer android debug deploy run
```

### Using python-for-android

```bash
pip install python-for-android

p4a apk --private . \
    --package=com.example.myapp \
    --name "My App" \
    --version 0.1 \
    --bootstrap=sdl2 \
    --requirements=python3,kivy,pyandroid \
    --permission INTERNET
```

## 🧪 Examples

### Calculator App

A full calculator with GUI: [pyandroid-calculator-app](https://github.com/subhobhai943/pyandroid-calculator-app)

### Todo List App

```python
from pyandroid import AndroidApp, Activity
from pyandroid.ui import LinearLayout, Button, EditText, TextView

class TodoActivity(Activity):
    def __init__(self):
        super().__init__("TodoActivity")
        self.todos = []
    
    def on_start(self):
        layout = LinearLayout("main", orientation="vertical")
        
        # Input area
        self.input_field = EditText("todo_input", hint="Enter task")
        layout.add_view(self.input_field)
        
        # Add button
        add_btn = Button("add_btn", "Add Task")
        add_btn.set_on_click_listener(self.add_todo)
        layout.add_view(add_btn)
        
        # Todo list display
        self.todo_display = TextView("todos", "No tasks yet")
        layout.add_view(self.todo_display)
        
        self.add_view("main", layout)
    
    def add_todo(self, view):
        task = self.input_field.get_text()
        if task:
            self.todos.append(task)
            self.input_field.set_text("")
            self.update_display()
    
    def update_display(self):
        text = "\n".join(f"{i+1}. {todo}" for i, todo in enumerate(self.todos))
        self.todo_display.set_text(text or "No tasks yet")

app = AndroidApp("Todo List", "com.example.todo")
app.register_activity("main", TodoActivity)
app.start_activity("main")
app.run()
```

## 🧰 Testing

PyAndroid includes a comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=pyandroid tests/

# Run specific test file
pytest tests/test_core.py
```

## 📝 License

This project is licensed under the **PyAndroid Custom License v1.0**.

### Key Points:
- ✅ Free for personal and educational use
- ✅ Open source requirement for derivative works
- ✅ Attribution required
- ❌ Commercial use requires permission

See [LICENSE](LICENSE) file for complete terms.

For commercial licensing: contact the maintainer

## 🛣️ Roadmap

### v1.3 (Planned)
- [ ] WebView component
- [ ] SQLite database integration
- [ ] Enhanced animation support
- [ ] More layout types

### v1.4 (Future)
- [ ] Push notifications
- [ ] Camera and media access
- [ ] Sensor integration
- [ ] Background services
- [ ] Material Design components

### v2.0 (Vision)
- [ ] Hot reload support
- [ ] Visual UI builder
- [ ] Plugin system
- [ ] Cloud backend integration

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📊 Stats

- 👨‍💻 **Actively Maintained**: Regular updates and improvements
- 📚 **Well Documented**: Comprehensive guides and API docs
- ✅ **Tested**: High test coverage
- 🔒 **Stable API**: Semantic versioning
- 👥 **Community**: Growing community of developers

## ❓ FAQ

**Q: Can I build real Android apps with this?**  
A: Yes! PyAndroid uses Kivy as a backend which can compile to native Android APKs.

**Q: Do I need to know Java?**  
A: No! Write everything in Python.

**Q: Is it production-ready?**  
A: PyAndroid is in beta. It's suitable for learning, prototyping, and small projects.

**Q: Can I publish to Google Play?**  
A: Yes! Apps built with PyAndroid can be published to app stores.

**Q: What's the performance like?**  
A: Good for most use cases. Performance-critical sections can use Cython.

## 📞 Support

- 🐛 [Report Bugs](https://github.com/subhobhai943/pyandroid-dev/issues)
- 💡 [Request Features](https://github.com/subhobhai943/pyandroid-dev/issues/new)
- 💬 [Discussions](https://github.com/subhobhai943/pyandroid-dev/discussions)
- 📖 [Wiki](https://github.com/subhobhai943/pyandroid-dev/wiki)
- ⭐ [Star this repo](https://github.com/subhobhai943/pyandroid-dev)

## 📚 Resources

- [Official Documentation](https://github.com/subhobhai943/pyandroid-dev/wiki)
- [Tutorial Series](https://github.com/subhobhai943/pyandroid-dev/wiki/Tutorials)
- [Example Apps](https://github.com/subhobhai943/pyandroid-dev/tree/main/examples)
- [API Reference](https://github.com/subhobhai943/pyandroid-dev/wiki/API-Reference)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

## 🌟 Star History

If you find PyAndroid useful, please star the repository! ⭐

## 🚀 Built With PyAndroid

Showcase your app! Open an issue to add your project here.

## 📝 Changelog

### v1.2.0 (2025-11-09)
- ✨ Added comprehensive test suite
- 📦 Prepared for PyPI deployment
- 📝 Added custom license
- 🚀 Added GitHub Actions CI/CD
- 📖 Enhanced documentation
- 🐛 Bug fixes and improvements

### v1.1.0 (2025-11-09)
- ✨ Added Kivy backend for GUI rendering
- 📱 Real graphical interface support
- 🚀 Cross-platform desktop and Android support
- 📖 Updated documentation

### v1.0.0 (2024-10-24)
- 🎉 Initial release
- 📦 Core Android components (App, Activity, Intent)
- 🎨 Complete UI framework (Views, Layouts, Widgets)
- 🛠️ Utility classes (Logger, FileManager, NetworkManager)

---

<div align="center">

**Made with ❤️ by [Subhobhai](https://github.com/subhobhai943)**

[⭐ Star](https://github.com/subhobhai943/pyandroid-dev) · [🐛 Report Bug](https://github.com/subhobhai943/pyandroid-dev/issues) · [✨ Request Feature](https://github.com/subhobhai943/pyandroid-dev/issues/new)

</div>
