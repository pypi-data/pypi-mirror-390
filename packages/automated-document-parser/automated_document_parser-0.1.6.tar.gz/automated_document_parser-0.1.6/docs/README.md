Documentation
=============

This directory contains the source files for building the Automated Document Parser documentation using Sphinx.

Building the Documentation
---------------------------

To build the HTML documentation:

```bash
# From the project root
make docs

# Or from the docs/ directory
cd docs
make html
```

The generated HTML files will be in `docs/_build/html/`.

Viewing the Documentation
--------------------------

After building, you can:

1. **Open directly in browser:**
   ```bash
   open docs/_build/html/index.html
   ```

2. **Start a local server:**
   ```bash
   make docs-serve
   # Then open http://localhost:8000 in your browser
   ```

Documentation Structure
-----------------------

- `conf.py` - Sphinx configuration file
- `index.rst` - Main documentation homepage
- `api.rst` - Complete API reference with autodoc
- `modules.rst` - Auto-generated module documentation
- `_static/` - Static files (CSS, images, etc.)
- `_templates/` - Custom templates
- `_build/` - Generated documentation (not in git)

Makefile Commands
-----------------

From the project root:

- `make docs` - Build HTML documentation
- `make docs-clean` - Clean build directory
- `make docs-serve` - Start local documentation server

From the docs/ directory:

- `make html` - Build HTML documentation
- `make clean` - Clean build directory
- `make help` - Show all available commands

Sphinx Extensions
-----------------

The documentation uses these Sphinx extensions:

- **autodoc** - Auto-generate docs from docstrings
- **napoleon** - Support for Google and NumPy style docstrings
- **viewcode** - Add links to highlighted source code
- **intersphinx** - Link to other project documentation
- **autosummary** - Generate autodoc summaries

Theme
-----

Uses the [Read the Docs Sphinx Theme](https://github.com/readthedocs/sphinx_rtd_theme).

To install: `uv pip install sphinx-rtd-theme`

Contributing to Documentation
------------------------------

When adding new modules or functions, make sure to:

1. Write clear docstrings using Google or NumPy style
2. Include parameter types and return types
3. Add usage examples where appropriate
4. Rebuild docs to verify formatting: `make docs`

Hosting
-------

The documentation can be easily hosted on:

- **Read the Docs** - Connect your GitHub repo
- **GitHub Pages** - Use `docs/_build/html/` directory
- **Any static hosting** - Deploy the `_build/html/` folder
