# Templated Generator
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![Build Status](https://app.travis-ci.com/k5md/Templated-Generator.svg?token=ZSWp3q2qzbTb4nzaxqWy&branch=master)](https://app.travis-ci.com/k5md/Templated-Generator) 
[![tempgen.png](https://s9.gifyu.com/images/tempgen.png)](https://gifyu.com/image/GfBa)

Templated generator is a utility, that allows users generate files from templates with embedded template entries that could be edited and automatically transformed, saving time that would be otherwise spend on manually editing generic documents.

The project includes python module, available on pypi, for use inside python scripts, cli and gui applications to edit template entries and quickly generate documents.

## Template entries
Generally, template entries are stringified and enclosed in double curly brackets valid JSON objects. Minimal template entry contains id and value properties. Entry ids can be not unique and for each entry, the value specified as replacement will be substituted after transforms.

### Entry object properties
| property name  | type   | required | description |
| :--------  | :----  | :------- | :---------- |
| id | string | yes | id used to reference entry in replacements|
| title | string | no | human-readable title that will be used to represent entry field in tempgen gui|
| value | string | yes | default value that will be used as replacement if no changes are made|
| pre | array of objects | no | array of transform objects that will be applied to value property before it becomes available for editing|
| post | array of objects | no | array of transform objects that will be applied to value property on generated document save|
| group | string | no | group tag name, entries with equal group property value will be grouped together in tempgen gui
| order | string | no | order number, used to determine entry position among other group entries in tempgen gui, entries with lower order value will appear earlier
| autocomplete | object | no | specifies which suggestions should be displayed on user input in entry representation in tempgen_gui

### Transform object properties
| property name  | type   | required | description |
| :--------  | :----  | :------- | :---------- |
| fn | string | yes | name of transform function|
| args | array of strings | no | human-readable title that will be used to represent entry field in tempgen gui|

### Autocomplete object properties
| property name  | type   | required | description |
| :--------  | :----  | :------- | :---------- |
| external | string | no | full name of json file (must be in the same directory as the template it is referenced from) containing array of autocomplete suggestion strings, used to fill data property|
| data | array of strings | no | list of values that will be used in as suggestions for entry value in tempgen gui|

## Getting Started
### Tempgen GUI/CLI standalone executables
* Download latest tempgen_gui/tempgen_cli [release](https://github.com/k5md/Templated-Generator/releases/latest)
* Unpack archive to any directory
* Run tempgen_gui/tempgen_cli binary
### Installation as module
```
pip install tempgen
```

#### Usage
```python
from tempgen.module import Tempgen

t = Tempgen() # create new independent tempgen instance

t.transforms.keys() # get list of supported transforms, you can add new on the fly, by setting t.transforms dictionary key to desired function name and value to this function
# dict_keys(['append', 'inverted_date', 'ru_date_month_as_string_year', 'ru_monetary_string_replace', 'ru_monetary_as_string', 'ru_monetary_ending_append'])

t.parsers.keys() # get list of supported file extensions, refer to documentation on how to add new extensions support
# dict_keys(['.docx', '.xlsx', '.md', '.txt', '.odt', '.ods'])

t.load_template(absolute_path_to_template) # parse template

t.get_templates() # get list of loaded templates

t.get_fields() # get reference to parsed entries

t.save_result(absolute_path_to_template, target_name_without_extension, { "id_from_template_text": "desired value" })
```

## Development
### Environment setup
1.  Install Python 3.6+
2.  Install `virtualenv`
    ```sh
    pip install virtualenv
    ```
3.  Clone this project
4.  From project directory, run
    ```sh
    virtualenv .env
    ```
    **Note**: This will create a virtual environment using the Python version
    that `virtualenv` was run with (which will be the version it was installed
    with). To use a specific Python version, run:
    ```sh
    virtualenv --python=<path_to_other_python_version> .env
    # For example, this might look like
    virtualenv --python=/usr/bin/python3.6 .env
    ```
5.  Assuming you are using the `bash` shell, run:
    ```sh
    source .env/bin/activate
    ```
    For other shells, see the other `activate.*` scripts in the `.env/bin/`
    directory. If you are on Windows, run:
    ```sh
    .env\Scripts\activate.bat
    ```
6.  Install all of the required packages using
    ```sh
    pip install -r requirements.txt
    ```

### Module/cli/gui code running
With virtual environment active, execute one of the following commands from **src** project directory:
```sh
python -m tempgen
python -m tempgen_cli
python -m tempgen_gui
```

### Testing
This project uses pytest and mostly relies on snapshot testing. To trigger tests run
```sh
pytest
```
optionally with -vv and -s flags for verbosity and prints.
**Note**: After each code modification that presumes expected generated output file changes, update snapshots by running
```sh
pytest --snapshot-update
```

### Creating portable executables
1. Enter the virtual environment (run `source .env/bin/activate` or OS/shell equivalent).
2.  Run the following command to create bundles with binaries for tempgen_cli and tempgen_gui in project's dist directory
    ```sh
    python package.py
    ```

## Contributions
PR are always welcome!