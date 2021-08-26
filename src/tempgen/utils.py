import os
import types
import functools
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

def has(l , key, value):
    """Check if list has dict with matching key-value pair

    Parameters
    ----------
    l : List[Dict[str, Any]]
        List to check for matches
    key : str
        Key to find in list's dictionaries
    value : Any
        Value to be compared with value in suitable key-value pair in each dictionary in list

    Returns
    -------
    bool
        True if list has dictionary with key-value pair matching given key and value, False otherwise.
    """
    for item in l:
        if item[key] == value:
            return True
    return False

def split_by_key_presense(l, key):
    """Split list of dictionaries into two lists based on key presense

    Parameters
    ----------
    l : List[Dict[str, Any]]
        List to split
    key : str
        Key to find in list's dictionaries

    Returns
    -------
    Tuple[List[Any], List[Any]]
        First list in tuple containing l's dictionaries that have given key, second list contain l's dictionaries that don't
    """
    present, missing = [], []
    for item in l:
        present.append(item) if property in item else missing.append(item)
    return present, missing

def copy_func(f):
    """Copy function

    Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)

    Parameters
    ----------
    f : callable
        Function to copy

    Returns
    -------
    callable
        The exact independent copy of provided function
    """
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g

def make_path(d, *paths):
    """Create nested dictionaries in path in dictionary
    
    Parameters
    ----------
    d : Dict[str, Any]
        Provided dictionary
    
    *args:
        Variable length list of path segments to create if not present

    Returns
    -------
    Dict
        Dict with nested dicts with paths items as keys

    Raises
    ------
    AttributeError
        If path segment already exists on the same level of provided dictionary AND is not a dictionary

    Examples
    --------
    >>> test = { "foo": { "baz": 42 } }
    >>> make_path(test, "foo", "bar", "baz")
    {}
    >>> test
    {'foo': {'baz': 42, 'bar': {'baz': {}}}}
    """
    while paths:
        key, *paths = paths
        d = d.setdefault(key, {})
    return d


def extract_zip(source_path, target_path):
    """Extract zip archive
    
    Parameters
    ----------
    source_path : str
        Path to archive to be extracted
    
    target_path : str
        Path to directory to extract archive content
    """
    with ZipFile(source_path, 'r') as zip_object:
        file_names = zip_object.namelist()
        for file_name in file_names:
            zip_object.extract(file_name, target_path)

def make_zip(source_path, target_path):
    """Create zip archive with only related paths (source_path > files or directories)
    
    Parameters
    ----------
    source_path : str
        Path to directory to be archived
    
    target_path : str
        Path (with file name) where to store resulting archive
    """
    source_path_last = source_path.split(os.sep)[-1] # relative path for zipf arcname construction
    zipf = ZipFile(target_path, 'w', ZIP_DEFLATED)
    for folder_name, subfolders, file_names in os.walk(source_path):
        for file_name in file_names:
            file_path = os.path.join(folder_name, file_name)
            segments = file_path.split(os.sep)
            archive_path = segments[segments.index(source_path_last):]
            zipf.write(file_path, arcname=os.sep.join(archive_path[1:]))
    zipf.close()

def fix_tk_file_path(incorrect_path):
    """Fix issue when tk.filedialog methods (like askdirectory) yield file paths with incorrect separators using slashes instead of backslashes on Windows

    Parameters
    ----------
    incorrect_path : str
        String using forward slashes like 'C:/Users/Foo/bar/baz'
    
    Returns
    -------
    str
        Correct platform-dependent path with os.sep as separator
    """
    return str(Path(incorrect_path).resolve())
