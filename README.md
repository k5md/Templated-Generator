# Templated Generator
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Build Status](https://app.travis-ci.com/k5md/Templated-Generator.svg?token=ZSWp3q2qzbTb4nzaxqWy&branch=master)](https://app.travis-ci.com/k5md/Templated-Generator) 
[![tempgen_illustration.png](https://gifyu.com/images/tempgen_illustration.png)](https://gifyu.com/image/S74q3)

Templated generator is a utility, that allows users generate files from templates with embedded template entries that could be edited and automatically transformed, saving time that would be otherwise spend on manually editing generic documents.

The project includes python module, available on pypi, for use inside python scripts, cli and gui applications to edit template entries and quickly generate documents.

## Template entries
Generally, template entries are stringified and enclosed in double curly brackets valid JSON objects. Here is an example:
```
{{{"id": "total", "title": "Total cost", "value": "2500", "post": [{"fn": "append", "args": [" U.S. Dollars"]}], "group": "primary", "order": "1"}}}
```
Minimal template entry contains id and value properties. Entry ids can be not unique and for each entry, the value specified once as replacement will be substituted and transforms (for respective entry) will be applied. This allows to edit value associated with id encountered multiple times over multiple templates only once.
For instance loaded templates can contain:
```
{{{"id": "total", "value": "2500", "post": [{"fn": "append", "args": [" U.S. Dollars"]}]}}}
{{{"id": "total", "value": "2500", "post": [{"fn": "append", "args": ["$"]}]}}}
{{{"id": "total", "value": "2500"}}}
```
In GUI application all three will be represented by one input with default value of "2500". Given replacements dictionary (for cli and using as module) of { "total": "42" }, or if input in this field equals "42" (for gui application), these will be represented in generated documents as
```
42 U.S. Dollars
42$
42
```
**Notes**:
- when creating templates in Microsoft Office [disable smart quotes](https://support.microsoft.com/en-us/office/smart-quotes-in-word-702fc92e-b723-4e3d-b2cc-71dedaf2f343) since only straight quotation marks are allowed in template entries
- for template entries to be correctly imported and substituted in MS/Open office documents, **whole** template entry string, for instance ```{{{"id": "total", "value": "2500"}}}```, must have consistent formatting

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
Transforms available by default are listed [here](https://github.com/k5md/Templated-Generator/blob/master/src/tempgen/transforms.py) .
These are functions, that are applied on "value" property sequentially either
* when template is loaded, if transform is in "pre" list
* when generated document is being saved, if transform is in "post" list

Transforms are provided with value (from entry) automatically, additional arguments could be provided via "args" array.
**Note**: When using as a module, one can easily modify the dictionary by changing tempgen instance 'transforms' attribute
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
To install from [pypi](https://pypi.org/project/tempgen/):
```
pip install tempgen
```

#### Usage as module
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

### Supported extensions
- docx
- xlsx
- md
- txt
- odt
- ods

## Development
### Environment setup
1.  Install Python 3.7+
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
This project employs pyinstaller to create binaries. To generate executables from sources on your PC:
1. Enter the virtual environment (run `source .env/bin/activate` or OS/shell equivalent).
2.  Run the following command to create bundles with binaries for tempgen_cli and tempgen_gui in project's dist directory
    ```sh
    python package.py
    ```
Generated archives will be placed in **artifacts** directory
### Packaging module
Run the following command to package tempgen module:
```sh
python -m pip install --upgrade build
python -m build
```
Generated archive and .whl package will be placed in **dist** directory.

### Generating documentation
Run the following command to generate updated documentation from collected docstrings and place it in **docs** directory:
```sh
pdoc src\tempgen --output-dir docs -d numpy
```

## Contributions
PR are always welcome!
