from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="custom-ui-pyqt6",
    version="1.0.3",
    author="CrypterENC",
    author_email="a95899003@gmail.com",
    description="Modern PyQt6 UI components with glassmorphism effects, smooth animations, and 21 customizable widgets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/custom-ui-pyqt6",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Desktop Environment :: Window Managers",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.0.0",
    ],
    keywords=[
        "pyqt6", "qt6", "ui", "gui", "components", "widgets",
        "glassmorphism", "modern", "design", "animations",
        "buttons", "forms", "dialogs", "menus", "scrollbars",
        "textarea", "checkbox", "radiobutton", "slider", "progressbar",
        "tabs", "cards", "badges", "spinner", "toast", "tooltip", "accordion",
        "frameless", "customizable", "themeable", "solid-colors",
        "desktop-application", "cross-platform"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/custom-ui-pyqt6/issues",
        "Source": "https://github.com/yourusername/custom-ui-pyqt6",
        "Documentation": "https://github.com/yourusername/custom-ui-pyqt6#readme",
        "Examples": "https://github.com/yourusername/custom-ui-pyqt6/tree/main/examples",
    },
)
