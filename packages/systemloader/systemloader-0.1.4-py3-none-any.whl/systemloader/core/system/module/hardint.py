from typing import Any
import re


# Оставить одни числа
def only_digital(s: str):
    return re.sub(r"\D", "", s)


# Преобразование строки в int, даже если строка без чисел!
def hardint(s: Any) -> int:
    res = 0
    if isinstance(s, str):
        if s_digital := only_digital(s):
            res = int(s_digital)
    elif isinstance(s, (float, int)):
        res = int(s)
    return res
