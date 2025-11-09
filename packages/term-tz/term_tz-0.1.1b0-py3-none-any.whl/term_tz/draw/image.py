# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from PIL import Image
from typing import Optional

from .utils import render_image
from ..types import ImgFillingModeName


def printable_image(
    img_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    mode: ImgFillingModeName = "half-color",
    charset: str = "@%#*+=-:. "
) -> str:
    r"""
    Convert an image file to a string representation based on the specified mode.

    Parameters
    ----------
        img_path : str
            Path to the image file.

        width : Optional[int], default to `None`
            Width of the rendered image.
            - `None`: Use original width, unless `height` is specified to maintain aspect ratio.

        height : Optional[int], default to `None`
            Height of the rendered image.
            - `None`: Use original height, unless `width` is specified to maintain aspect ratio.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode. ~see `render_image` for details.

        charset : str, default to `"@%#*+=-:. "`
            Characters used for `"ascii"` representation, ordered from darkest to lightest.

    Returns
    -------
        str
            String representation of the rendered image, use print() to display.
    """
    img = Image.open(img_path)

    aspect_ratio = img.height / img.width
    if height is not None or width is not None:
        if height is None and width is not None:
            height = int(aspect_ratio * width)
        elif width is None and height is not None:
            width = int(height / aspect_ratio)
        img = img.resize((width, height))

    return render_image(img, mode=mode, charset=charset)
