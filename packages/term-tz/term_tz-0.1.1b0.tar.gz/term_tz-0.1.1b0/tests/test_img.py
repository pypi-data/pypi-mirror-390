import pytest
import sys
sys.path.insert(0, "./src")

from term_tz import printable_image


print(printable_image(
    "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
    mode="ascii",
    height=-1
))


print(printable_image(
    "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
    mode="half-color",
    height=30
))
