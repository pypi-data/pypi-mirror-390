# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from typing import (Any, Optional, Iterable, Union)

from .types import (ColorName, StyleName)


# code of colors
_COLOR_CODE = {
    "d": 0,  # dark/black
    "r": 1,  # red
    "g": 2,  # green
    "y": 3,  # yellow
    "b": 4,  # blue
    "m": 5,  # magenta
    "c": 6,  # cyan
    "w": 7,  # white
}
# code of styles
_STYLE_CODE = {
    "bold": 1,
    "dim": 2,
    "italic": 3,
    "udl": 4,
    "blink": 5,
    "selected": 7,
    "disappear": 8,
    "del": 9
}


def ctext(
    text: Any,
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
) -> "ColorStr":
    r"""
    Generate a colored string for terminal output.

    NOTE: The actual colored string is like `\033[43;1mtest\033[0m`.

    Parameters
    ----------
        text : Any
            The text content to be colored.

        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            - _ColorName_: `Basic 8 color` OR `Light 8 color`, compatible with older terminals;

            NOTE: _ColorName_: `d`(black); `r`(red); `g`(green); `y`(yellow); `b`(blue); `m`(magenta); `c`(cyan); `w`(white). Prefix `l` means Light 8 color.

            - _int_: `256 color`, compatible with most terminals;

            NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.

            - _Iterable[int]_: `True color`, compatible with modern terminals.

            NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as `fg`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.

            NOTE: _StyleName_: `bold`, `dim`, `italic`, `udl`, `blink`, `selected`, `disappear`, `del`.

    Returns
    -------
        ColorStr
            The colored string with ANSI escape codes. Usage same as `str`, with extra property `plain` to get the plain text.
    """
    return ColorStr(text, fg=fg, bg=bg, styles=styles)


class ColorStr(str):
    r"""
    A string class that supports ANSI color and style formatting while preserving plain text.

    NOTE: Usage same as `str`, with extra property `plain` to get the plain text.
    """
    def __new__(
        cls,
        text: Any,
        fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        styles: Optional[Iterable[StyleName]] = None
    ):
        plain_text = str(text)
        if plain_text:
            ansi_text = ColorStr._colorize(
                plain_text,
                fg=fg,
                bg=bg,
                styles=styles if styles is not None else []
            )
        else:
            ansi_text = plain_text

        obj = super().__new__(cls, ansi_text)

        return obj

    def __init__(
        self,
        text: Any,
        fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        styles: Optional[Iterable[StyleName]] = None
    ):
        self.__plain = str(text)
        super().__init__()

    @staticmethod
    def _parse_color(
        c: Union[ColorName, int, Iterable[int]],
        is_fg: bool
    ) -> str:
        parse = ""
        if isinstance(c, str):
            # Basic 8 color OR Light 8 color
            if c in _COLOR_CODE:
                # Basic 8 color
                parse = ("3" if is_fg else "4") + str(_COLOR_CODE[c])
            elif c.startswith("l") and c[1:] in _COLOR_CODE:
                # Light 8 color
                parse = ("9" if is_fg else "10") + str(_COLOR_CODE[c[1:]])
        elif isinstance(c, int) and 0 <= c <= 255:
            # 256 color
            parse = ("38" if is_fg else "48") + f";5;{c}"
        elif isinstance(c, Iterable):
            # True color
            rgb = (list(c) + [0, 0, 0])[:3]
            if all(0 <= val <= 255 for val in rgb):
                parse = ("38" if is_fg else "48") + f";2;{rgb[0]};{rgb[1]};{rgb[2]}"

        return parse

    @staticmethod
    def _colorize(
        text: str,
        fg: Optional[Union[ColorName, int, Iterable[int]]],
        bg: Optional[Union[ColorName, int, Iterable[int]]],
        styles: Iterable[StyleName]
    ) -> str:
        # styles
        if isinstance(styles, Iterable):
            font_styles = ";".join(str(_STYLE_CODE[s]) for s in styles if s in _STYLE_CODE)
        else:
            font_styles = ""
        # foreground
        foreground = "" if fg is None else ColorStr._parse_color(fg, is_fg=True)
        # background
        background = "" if bg is None else ColorStr._parse_color(bg, is_fg=False)
        # combine
        codes = [code for code in [font_styles, foreground, background] if code]

        return f"\033[{';'.join(codes)}m{text}\033[0m"

    @property
    def plain(self) -> str:
        r"""
        The plain text without ANSI formatting.
        """
        return self.__plain
