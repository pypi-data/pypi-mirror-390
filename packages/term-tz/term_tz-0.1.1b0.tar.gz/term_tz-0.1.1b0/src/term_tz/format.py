# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from typing import (Any, Optional, Mapping, Sequence)

from .color import ctext


def dict_print(
    target: Mapping[str, Any],
    omit_items: Sequence[str] = [],
    title: str = "",
    class_name: Optional[str] = None,
    display: bool = True
):

    if isinstance(target, Mapping) and target:
        str_return = ctext(title, fg="d", bg="y", styles={"bold"})
        if class_name:
            demo1 = ctext("[param]", fg="d", bg="g", styles={"bold"})
            demo2 = ctext("[_param]", fg="d", bg="w", styles={"bold"})
            demo3 = ctext("[_CurClass__param]", fg="d", bg="w", styles={"dim"})
            demo4 = ctext("[_FatherClass__param]", fg="w", bg=None, styles={"dim"})
            demo = f"\n    {demo1}  {demo2}  {demo3}  {demo4}"
        else:
            demo = ""
        str_return = f"  >>>\n  {str_return}{demo}"
        for idex, key in enumerate(target, start=1):
            value = target[key]
            v_type_str = ctext(type(value).__name__, fg="c", styles={"italic"})
            if class_name:
                if key[0] != "_":
                    # param
                    param_name = key
                    font = "d"
                    back = "g"
                    style = "bold"
                else:
                    key = key[1:]
                    try:
                        param_name = key.split("__")[1]
                        if key.split("__")[0] == class_name:
                            # _CurClass__param
                            font = "d"
                            back = "w"
                            style = "dim"
                        else:
                            # _FatherClass__param
                            font = "w"
                            back = None
                            style = "dim"
                    except IndexError:
                        if key[0] == "_":
                            # __param
                            param_name = key[1:]
                            font = "d"
                            back = "w"
                            style = "dim"
                        else:
                            # _param
                            param_name = key
                            font = "d"
                            back = "w"
                            style = "bold"
            else:
                param_name = key
                font = "d"
                back = "w"
                style = "bold"
            key_str = ctext(f"[{param_name}]", fg=font, bg=back, styles={style})
            if param_name in omit_items and value:
                value = ctext("PLACEHOLDER", styles={"udl"})

            str_return = f"{str_return}\n#{idex}{' ' if idex<10 else ''} {key_str}{v_type_str}: {value}"
        str_return = f"{str_return}\n  <<<"
    else:
        str_return = ""
    if display:
        print(str_return)

    return str_return


def list_print(target: Sequence[Any], display: bool = True):
    r"""
    Print a list with index for each item.

    Parameters
    ----------
        target : Sequence[Any]
            The Sequence to be printed.

        display : bool, default to `True`
            Whether to print the formatted string to the terminal.

    Returns
    -------
        str
            The formatted string representation of the list.
    """
    lines = []
    if target and isinstance(target, Sequence):
        indent = len(str(len(target)))
        for idex, item in enumerate(target, start=1):
            lines.append(f"#{str(idex).zfill(indent)} {item}")
    result = "\n".join(lines)

    if display and result:
        print(result)

    return result
