"""
Plugin functions and utilities for FigWizz
"""

import importlib

def check_optional_import(package_name):
    """
    Check if an optional package is installed.
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False