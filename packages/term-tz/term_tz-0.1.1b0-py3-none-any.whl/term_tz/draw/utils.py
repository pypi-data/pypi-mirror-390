# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from PIL import (Image, ImageChops)
import numpy as np
from typing import (Tuple, List, Union, Iterable)

from ..color import ctext
from ..types import ImgFillingModeName


VALID_MODES = ("ascii", "color", "half-color", "gray", "half-gray")


def render_image(
    img: Image.Image,
    mode: ImgFillingModeName = "half-color",
    charset: str = "@%#*+=-:. "
) -> str:
    r"""
    Render an image (`PIL.Image.Image`) into a string representation based on the specified mode.

    Parameters
    ----------
        img : Image.Image
            The PIL Image to be rendered.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode, which can be one of the following:
            - `"ascii"`: Render using ASCII characters, mapping pixel brightness to characters in `charset`.
            - `"color"`: Render using full block characters with color.
            - `"half-color"`: Render using half block characters with color, combining two pixels vertically.
            - `"gray"`: Render using full block characters in grayscale.
            - `"half-gray"`: Render using half block characters in grayscale, combining two pixels vertically.

        charset : str, default to `"@%#*+=-:. "`
            Characters used for `"ascii"` representation, ordered from darkest to lightest.

    Returns
    -------
        str
            String representation of the rendered image, use print() to display.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Unknown mode(ImgFillingModeName): {mode!r}. Valid Modes: {VALID_MODES}")

    is_color = "color" in mode
    if not is_color:
        # Convert to grayscale
        img = img.convert("L")
    pixel_arr = np.array(img)
    height, width = pixel_arr.shape[:2]

    out_lines: List[str] = []
    if mode.startswith("half-"):
        # Mode: `half-color` or `half-gray`
        for y in range(0, height, 2):
            upper_row = pixel_arr[y]
            lower_row = pixel_arr[y + 1] if (y + 1) < height else None
            line_str = ""
            for x in range(width):
                # fore
                if is_color:
                    # Mode: `half-color`
                    fore = upper_row[x]
                else:
                    # Mode: `half-gray`
                    upper = int(upper_row[x])
                    fore = (upper, upper, upper)
                # back
                if lower_row is not None:
                    if is_color:
                        # Mode: `half-color`
                        back = lower_row[x]
                    else:
                        # Mode: `half-gray`
                        lower = int(lower_row[x])
                        back = (lower, lower, lower)
                else:
                    back = None
                line_str += ctext("\u2580", fg=fore, bg=back)
            out_lines.append(line_str)
    elif mode == "ascii":
        # Mode: `ascii`
        char_arr = np.array(list(charset))
        pixel_arr_max = pixel_arr.max()
        pixel_arr_min = pixel_arr.min()
        if pixel_arr_max == pixel_arr_min:
            indices = np.zeros_like(pixel_arr, dtype=int)
        else:
            indices = (pixel_arr - pixel_arr_min) * (len(charset) - 1) // (pixel_arr_max - pixel_arr_min)
        out_lines = ["".join(char_arr[indices[row]]) for row in range(height)]
    else:
        # Mode: `ascii`, `color`, `gray`
        for row in pixel_arr:
            line_str = ""
            for pixel_val in row:
                if mode == "ascii":
                    char_index = pixel_val * (len(charset) - 1) // 255
                    line_str += charset[char_index]
                else:
                    line_str += ctext(
                        " ",
                        bg=pixel_val if is_color else (pixel_val, pixel_val, pixel_val)
                    )
            out_lines.append(line_str)

    return "\n".join(out_lines)


def create_binary_image(
    src: Union[Iterable, Image.Image],
    threshold: int = 128,
    upper_rgb: Tuple[int, int, int] = (255, 255, 255),
    lower_rgb: Tuple[int, int, int] = (0, 0, 0)
) -> Image.Image:
    r"""
    Create a binary image from the given source based on the specified threshold and RGB colors.

    Parameters
    ----------
        src : Union[Iterable, Image.Image]
            The source image data, which can be a 2-D or 3-D array-like structure or a PIL Image.

        threshold : int, default to `128`
            The threshold value to binarize the image.

        upper_rgb : Tuple[int, int, int], default to `(255, 255, 255)`
            The RGB color for pixels above the threshold.

        lower_rgb : Tuple[int, int, int], default to `(0, 0, 0)`
            The RGB color for pixels below and equal to the threshold.

    Returns
    -------
        Image.Image
            A PIL Image representing the binary image with specified RGB colors.
    """
    if isinstance(src, Image.Image):
        # as a PIL Image
        arr = np.array(src.convert("L"))
    else:
        arr = src if isinstance(src, np.ndarray) else np.array(src, copy=False)
        # Check array dimensions
        arr_shape = arr.shape
        if len(arr_shape) == 3:
            if arr_shape[-1] == 3:
                img = Image.fromarray(arr.astype(np.uint8), mode="RGB")
                arr = np.array(img.convert("L"))
            elif arr_shape[-1] == 1:
                arr = arr.reshape(arr_shape[0], arr_shape[1])
            else:
                raise ValueError(f"Input 3-D Array's Last Dimension Must Be 1 (Grayscale) Or 3 (RGB), Not {arr_shape[-1]}.")
        if len(arr_shape) != 2:
            raise ValueError(f"Input Array Must Be 2-D (Grayscale Image) Or 3-D (RGB Image), Not {arr_shape}.")

    arr = arr.astype(np.uint8)

    mask = arr > threshold
    upper = np.array(upper_rgb, dtype=np.uint8)
    lower = np.array(lower_rgb, dtype=np.uint8)

    rgb_arr = np.where(mask[..., None], upper, lower)

    return Image.fromarray(rgb_arr, mode="RGB")


def trim_image_border(img: Image.Image, value: int = 0):
    r"""
    Trim the border of the image that matches the specified value.

    Parameters
    ----------
        img : Image.Image
            The PIL Image to be trimmed.

        value : int, default to `0`
            The pixel value to be trimmed from the borders.

    Returns
    -------
        Image.Image
            The trimmed PIL Image.
    """
    bg = Image.new(img.mode, img.size, value)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    return img
