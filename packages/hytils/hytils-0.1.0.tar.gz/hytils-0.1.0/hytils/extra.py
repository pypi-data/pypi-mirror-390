import inspect
from typing import Type


def arg_list(model_class: type) -> list[str]:
    return [
        kw
        for kw in inspect.signature(model_class.__init__).parameters.keys()
    ][1:]


def swap_keys_values(d: Type[dict]) -> Type[dict]:
    """Swap keys/value of a dict.
    Warning, it owerwrites a key, value pair if already exists"""
    swapped: Type[dict] = type(d)()
    for k, v in d.items():
        if isinstance(v, list):
            swapped.update({x: k for x in v})
        else:
            swapped[v] = k
    return swapped
