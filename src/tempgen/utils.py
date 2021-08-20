import os
import types
import functools
from zipfile import ZipFile, ZIP_DEFLATED

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

def extract_zip(source_path, target_path):
    with ZipFile(source_path, 'r') as zip_object:
        file_names = zip_object.namelist()
        for file_name in file_names:
            zip_object.extract(file_name, target_path)

def make_zip(source_path, target_path):
    source_path_last = source_path.split(os.sep)[-1] # relative path for zipf arcname construction
    zipf = ZipFile(target_path, 'w', ZIP_DEFLATED)
    for folder_name, subfolders, file_names in os.walk(source_path):
        for file_name in file_names:
            file_path = os.path.join(folder_name, file_name)
            segments = file_path.split(os.sep)
            archive_path = segments[segments.index(source_path_last):]
            zipf.write(file_path, arcname=os.sep.join(archive_path[1:]))
    zipf.close()
