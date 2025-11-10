"""Setup configuration for PyAndroid library."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyandroid-dev",
    version="1.1.0",
    author="Subhobhai",
    author_email="sarkarsubhadip604@gmail.com",
    description="A Python library for creating Android applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/subhobhai943/pyandroid-dev",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies - none required
    ],
    extras_require={
        "gui": [
            "kivy>=2.0.0",
            "kivy[base]>=2.0.0",
        ],
        "all": [
            "kivy>=2.0.0",
            "kivy[base]>=2.0.0",
        ]
    },
    keywords="android python mobile app development kivy",
    project_urls={
        "Bug Reports": "https://github.com/subhobhai943/pyandroid-dev/issues",
        "Source": "https://github.com/subhobhai943/pyandroid-dev",
    },
)
