import types
import functools

def has(arr , key, value):
    for x in arr:
        if x[key] == value:
            return True

def split_by_property_presense(array, property):
    present, missing = [], []
    for item in array:
        present.append(item) if property in item else missing.append(item)
    return present, missing

def copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g

def make_path(my_dict: dict, *paths: str) -> dict:
    while paths:
        key, *paths = paths
        my_dict = my_dict.setdefault(key, {})
    return my_dict