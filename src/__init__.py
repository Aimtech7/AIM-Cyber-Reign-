"""
__init__.py — Source Package Initialiser
=========================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Marks the ``src/`` directory as a Python package so that
          other modules can be imported with ``from src import ...``.

Why this file exists:
    Python requires an __init__.py (even if empty) to treat a folder
    as an importable package.  We also expose key metadata here.
"""

# ── Package‑level metadata ────────────────────────────────────────────── #
__project__ = "AIM: Cyber Reign"   # human‑readable project name
__author__  = "Aimtech"            # project author / studio name
__version__ = "0.1.0"             # current semantic version
