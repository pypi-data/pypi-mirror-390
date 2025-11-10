# Masterblog‑core 📦

[![PyPI version](https://badge.fury.io/py/masterblog-core.svg)](https://pypi.org/project/masterblog-core/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/masterblog-core)](https://pepy.tech/project/masterblog-core)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Code style: PEP8](https://img.shields.io/badge/code%20style-PEP8-yellow)
![Status](https://img.shields.io/badge/status-learning--project-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📑 Table of Contents  

- [⚠️ Disclaimer](#-disclaimer)  
- [📝 Description](#-description)  
- [✨ Features](#-features)  
- [📁 Project Structure](#-project-structure)  
- [📦 Installation](#-installation)  
  - [⚡ Quick Start](#-quick-start)  
- [🚀 Usage](#-usage)  
- [🔖 Versioning](#-versioning)  
- [👥 Contributing](#-contributing)  
- [🏷️ Badges](#-badges)  
- [🔗 See Also](#-see-also)  
- [📄 License](#-license) 

---

## ⚠️ Disclaimer  
This project began as part of my learning journey during a multi‑month software engineering course.  

The original **Masterblog** repository included a Flask server and frontend. This fork, **Masterblog‑core**, strips away the web layer and focuses only on the reusable backend logic. The emphasis has shifted toward **packaging and redistribution** as a standalone Python library.  

- No new features have been added — in fact, the frontend has been removed.  
- The goal is to ensure the underlying models and storage still work as expected.  
- It remains a **learning project** and is **not intended for production use**.  

---

## 📝 Description  
**Masterblog‑core** provides the essential building blocks of a simple blogging system:  

- `Blog` and `Post` classes for managing posts.  
- JSON‑based persistence with auto‑incrementing IDs.  
- A lightweight storage layer (`filestore`, `sequence`).  

This package is designed for **reuse in other projects** or as a **learning reference** for object‑oriented design and Python packaging.  

---

## ✨ Features  
- ➕ Create new blog posts  
- ✏️ Update existing posts  
- ❌ Delete posts  
- ❤️ Like posts (with persistence)  
- 📦 JSON storage with auto‑increment IDs  
- 🔌 File‑path injection for flexible persistence  

---

## 📁 Project Structure  

```
.
├── .gitignore           # Ignore sensitive/generated files
├── LICENSE              # MIT license text
├── pyproject.toml       # Project metadata and dependencies
├── README.md            # Project documentation
└── src/                 # Main application source code
    └── masterblog_core
        ├── __init__.py  # Public API (Blog, Post, storage) 
        ├── models/      # Data models
        │   ├── blog.py  # Blog class managing posts
        │   └── post.py  # Post class with attributes and methods
        └── storage/     # Persistence layer
            ├── filestore.py  # JSON read/write helpers
            └── sequence.py   # Auto-increment ID handling
```

---

## 📦 Installation  

From PyPI:  
```bash
pip install masterblog-core
```

For local development:  
```bash
git clone https://github.com/paul-wosch/Masterblog-core.git
cd Masterblog-core
pip install -e .
```

### Requirements

- Python 3.10 or newer  
- No external dependencies beyond the Python standard library

### ⚡ Quick Start

```bash
pip install masterblog-core
````

```python
from masterblog_core import Blog

blog = Blog("blog.json", "sequence.json")
blog.add({"author": "Me", "title": "Hello", "content": "First post!"})
```

---

## 🚀 Usage  

After installation, you can import and use the package in Python:

```python
from pathlib import Path
from masterblog_core import Blog, Post

# Define file paths for persistence
PROJECT_ROOT = Path(__file__).resolve().parent
BLOG_FILE_PATH = (PROJECT_ROOT / "blog.json").resolve()
SEQUENCE_FILE_PATH = (PROJECT_ROOT / "sequence.json").resolve()

# Initialize Blog with file paths
my_blog = Blog(BLOG_FILE_PATH, SEQUENCE_FILE_PATH)

# Example usage
my_post = {
    "author": "Your Name",
    "title": "Hello World",
    "content": "This is my first post!",
    "likes": 0
}
my_blog.add(my_post)
```

---

## 🔖 Versioning  

The package version is defined once in **`pyproject.toml`** and exposed at runtime via  
`masterblog_core.__version__`. This is automatically synchronized using
`importlib.metadata`, so you only need to update the version in one place.

You can check the installed version programmatically:

```python
import masterblog_core
print(masterblog_core.__version__)
```

### How it works  

Inside `masterblog_core/__init__.py`, the version is resolved from the installed
package metadata:

```python
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("masterblog-core")
except PackageNotFoundError:
    # Fallback for local development when package metadata is not available
    __version__ = "0.0.0"
```

This ensures consistency between the distribution metadata and the runtime API.

---

## 👥 Contributing  
This project is primarily a learning exercise, but contributions, suggestions, or feedback are welcome. If you’d like to propose improvements:  
1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/your-feature`)  
3. Commit your changes (`git commit -m "feat: Add your feature"`)  
4. Push to the branch (`git push origin feature/your-feature`)  
5. Open a Pull Request  

---

## 🏷️ Badges

- **PyPI version** – latest release on PyPI  
- **Downloads** – monthly installs from PyPI (click for details on pepy.tech)  
- **Python** – minimum supported Python version  
- **Code style** – follows PEP8 guidelines  
- **Status** – indicates this is a learning project  
- **License** – MIT license

---

## 🔗 See Also

This package was extracted from the original [Masterblog](https://github.com/paul-wosch/Masterblog) project, 
which includes a Flask server and frontend.  
* Use **Masterblog‑core** if you want the reusable backend logic as a library.  
* Use **Masterblog** if you want the full web application with UI.

---

## 📄 License  
This project is licensed under the terms of the [MIT License](./LICENSE).  
See the LICENSE file for full details.