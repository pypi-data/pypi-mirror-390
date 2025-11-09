
import pytest
import sys
sys.path.insert(0, "./src")

from term_tz import ctext


for i in range(0, 256):
    
    a = ctext("\u2588", fg=(0, 0, i))

    print(a, end="")

    if (i + 1) % 32 == 0:
        print()
