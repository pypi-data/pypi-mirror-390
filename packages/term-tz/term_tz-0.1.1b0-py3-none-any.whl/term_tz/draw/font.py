# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

import os
import importlib.resources as pkg_resources
from PIL import (Image, ImageDraw, ImageFont)
from typing import (Tuple, Optional, Any, Union)

from . import fonts
from .fonts import FontName
from .utils import (render_image, create_binary_image, trim_image_border)
from ..types import ImgFillingModeName


def color_font(
    text: str,
    font: Union[FontName, str] = FontName.LLDISCO,
    mode: ImgFillingModeName = "half-color",
    trim_border: bool = False,
    charset: str = " #",
    fore_rgb: Tuple[int, int, int] = (255, 255, 255),
    back_rgb: Tuple[int, int, int] = (0, 0, 0),
    threshold: int = 5,
    font_size: int = 10,
    size: Optional[Tuple[int, int]] = None,
    left_top: Tuple[int, int] = (0, 0)
):
    r"""
    Render colored text based on a specified font into a string representation.

    Parameters
    ----------
        text : str
            The text to be rendered.

        font : Union[FontName, str], default to `FontName.LLDISCO`
            The font to be used for rendering the text.
            - `FontName` Enum: Use built-in fonts.
            - `str`: Path to a TTF/OTF font file.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode. ~see `render_image` for details.

        trim_border : bool, default to `False`
            Whether to trim the border of the rendered image.

        charset : str, default to `" #"`
            Characters used for `"ascii"` representation. The first character represents the background, and the last character represents the foreground.

        fore_rgb : Tuple[int, int, int], default to `(255, 255, 255)`
            RGB color for the foreground (text color).

        back_rgb : Tuple[int, int, int], default to `(0, 0, 0)`
            RGB color for the background.

        threshold : int, default to `5`
            Threshold for converting grayscale to binary image (0-255). Specifically, pixels with brightness above this value are considered foreground, and those below are background.

        font_size : int, default to `10`
            Size of the font.

        size : Optional[Tuple[int, int]], default to `None`
            Size of the image canvas as (width, height).
            - `None`: Automatically determine size based on text length and font size.

        left_top : Tuple[int, int], default to `(0, 0)`
            Left top position to start drawing text on the image canvas.

    Returns
    -------
        str
            String representation of the rendered colored text, use print() to display.
    """
    def _check(size: Any, default: Tuple[int, int]) -> Tuple[int, int]:
        if (isinstance(size, tuple)
                and len(size) == 2
                and all(isinstance(v, int) and v > 0 for v in size)):
            return size

        return default

    text = str(text)
    # size of font
    if not (isinstance(font_size, int) and font_size > 0):
        font_size = 10
    font_size = int(font_size)
    # size of the image canvas
    img_size = _check(size, (len(text) * font_size, font_size * 2))
    # left top position
    left_top = _check(left_top, (0, 0))

    img = Image.new("L", img_size, color=0)
    draw = ImageDraw.Draw(img)
    # font
    if os.path.isfile(font):
        try:
            pil_font = ImageFont.truetype(font, size=font_size)
        except Exception as e:
            raise ValueError(f"Font File '{font}' Load Error: {e}")
    elif isinstance(font, FontName):
        with pkg_resources.path(fonts, font.value) as font_path:
            pil_font = ImageFont.truetype(str(font_path), size=font_size)
    else:
        raise ValueError(f"Font '{font}' Not Supported. Please Provide A Valid TTF/OTF Font File Or Use FontName Enum.")

    draw.text(left_top, text, font=pil_font, fill=255)

    if trim_border:
        img = trim_image_border(img, value=0)

    binary_img = create_binary_image(
        img,
        threshold=threshold,
        upper_rgb=fore_rgb,
        lower_rgb=back_rgb
    )
    return render_image(binary_img, mode=mode, charset=charset)
