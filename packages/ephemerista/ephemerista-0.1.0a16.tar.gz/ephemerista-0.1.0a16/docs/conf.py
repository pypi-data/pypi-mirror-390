import os
import sys

# For some reason sphinx.ext.autodoc will see stale code when running under sphinx-autobuild.
# This problem does not exist with the normal sphinx-build command.
# TODO: Come up with an MWE and raise an issue in an appropriate place.
if sys.argv[0].endswith("sphinx-autobuild"):
    import importlib
    from pathlib import Path

    for path in Path("../src").rglob("*.py"):
        module_name = os.path.splitext(path.relative_to("../src"))[0].replace(os.sep, ".")
        if "__" in module_name:
            continue
        module = importlib.import_module(module_name)
        importlib.reload(module)


project = "Ephemerista"
author = "Libre Space Foundation"
project_copyright = "%Y, Libre Space Foundation"

html_title = "Ephemerista"
html_theme = "furo"
html_logo = "logo.webp"

latex_engine = "lualatex"

# Fix for "Too deeply nested" error in LaTeX
latex_elements = {
    "preamble": r"""
\usepackage{enumitem}
\setlistdepth{99}
""",
}

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.autodoc_pydantic",
]

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_json = False

source_suffix = [".rst", ".md"]

autodoc_default_options = {"exclude-members": "model_post_init, model_computed_fields"}

myst_heading_anchors = 3
