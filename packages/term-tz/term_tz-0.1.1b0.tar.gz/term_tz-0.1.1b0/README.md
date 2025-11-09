<div align="center">

<h2 id="title">term-tz</h2>

[![Build](https://github.com/tinchen777/term-tz/actions/workflows/tests.yml/badge.svg)](https://github.com/tinchen777/term-tz/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/term-tz.svg)](https://pypi.org/project/term-tz/)
![Python Versions](https://img.shields.io/pypi/pyversions/term-tz.svg)
![License](https://img.shields.io/github/license/tinchen777/term-tz.svg)
[![Pull Requests Welcome](https://img.shields.io/badge/pull%20requests-welcome-brightgreen.svg)](https://github.com/tinchen777/term-tz/pulls)

</div>

## About

A lightweight Python library for enhanced terminal display: simple text color/style conventions and image-to-terminal rendering.

- Python: 3.9+
- Runtime deps: Pillow (>=9,<11), NumPy (>=1.21,<2)

## Features

- :rocket Concise color/style names for terminal text.
- :rocket Image rendering in multiple modes: ASCII, color, half-color, gray, half-gray.
- :rocket Minimal dependencies and easy integration.

## Installation

Stable (once published):

```bash
pip install term-tz
```

## Quick Start

- Render an image in the terminal:

    ```python
    from term_tz import printable_image

    # ASCII art
    print(printable_image("example.jpg", width=80, mode="ascii"))

    # Half-block color (recommended for truecolor terminals)
    print(printable_image("example.jpg", width=80, mode="half-color"))
    ```

- Render some text with fonts in the terminal:

    ```python
    from term_tz import color_font, FontName

    # Borderless grayscale font
    print(color_font("Hello World!", font=FontName.LLDISCO,, mode="half-gray", trim_border=True))
    ```

## Image Modes

- ascii: monochrome ASCII using a density charset.
- color: colorized character fill.
- half-color: half-block characters with color (higher density, good visual quality).
- gray: grayscale characters.
- half-gray: half-block grayscale.

Tip: For best results, use a TrueColor-capable terminal and a monospaced font.

## Requirements

- Python >= 3.9
- Pillow >= 9.0, < 11
- NumPy >= 1.21, < 2.0

## License

See LICENSE in the repository.

## Links

- Homepage/Repo: https://github.com/tinchen777/term-tz.git
- Issues: https://github.com/tinchen777/term-tz.git/issues