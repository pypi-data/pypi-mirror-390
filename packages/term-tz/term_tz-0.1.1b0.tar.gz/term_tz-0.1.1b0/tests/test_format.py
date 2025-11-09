import pytest
import sys
sys.path.insert(0, "./src")

from term_tz import dict_print, list_print



d = {"a": 2, "b": [1, 2, 3, {"c": 4, "d": [5, 6, 7]}], "e": {"f": 8, "g": 9}}

l = [1, 2, 3, {"a": 4, "b": [5, 6, 7]}, [8, 9, 10], ""]

dict_print(d, omit_items=["b"], title="Test Dict Print", class_name=None)

list_print(l)

print(1)
