import pytest
import sys
sys.path.insert(0, "./src")

from term_tz import color_font, FontName



print(color_font(
    "Hello, Term-TZ!",
    # font="/data/tianzhen/my_packages/term-tz/src/term_tz/draw/fonts/LLDISCO_.TTF",
    font=FontName.LLDISCO,
    trim_border=True,
    mode="half-gray",
    font_size=10,
    fore_rgb=(255, 120, 0),
    back_rgb=(0, 120, 0)
    
))
