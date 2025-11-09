
from typing import (Any, Optional, Iterable, Union, Sequence)
from PIL import Image
import numpy as np


arr = np.random.randint(0, 256, size=(4, 4, 1))

print(arr.shape)

assert isinstance(arr, Iterable)


img = Image.fromarray(arr.astype(np.uint8), mode="L")



print(np.array(img))

print(img.mode)