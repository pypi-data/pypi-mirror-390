# src/term-tz/__init__.py
"""
term-tz
-------

A lightweight Python package for terminal display enhancements.

_Example:_
>>> from term_tz import color_str
"""
from .color import ctext
from .format import dict_print, list_print
from .draw import (
    color_font,
    printable_image,
    render_image,
    create_binary_image,
    FontName
)

__author__ = "Zhen Tian"
__version__ = "0.1.0"

__all__ = [
    "ctext",
    "FontName",
    "color_font",
    "printable_image",
    "render_image",
    "create_binary_image",
    "dict_print",
    "list_print"
]
