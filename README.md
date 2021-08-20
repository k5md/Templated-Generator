# Templated generator

## Virual Environments

This project runs in a _virtual environment_. See the [virtual environment] documentation for information on how this works.

## Using this Project

### Step 1: Install required programs

1.  Install Python 3.6+
2.  Install `virtualenv`
    ```sh
    pip install virtualenv
    ```

### Step 2: Create a new project
1.  Copy this project
2.  In a terminal, run
    ```sh
    virtualenv .env
    ```
    to set up a new virtual environment.

    **Note**: This will create a virtual environment using the Python version
    that `virtualenv` was run with (which will be the version it was installed
    with). To use a specific Python version, use
    ```sh
    virtualenv --python=<path_to_other_python_version> .env
    # For example, this might look like
    virtualenv --python=/usr/bin/python3.6 .env
    ```
    instead.
3.  Assuming you are using the `bash` shell, run
    ```sh
    source .env/bin/activate
    ```

    For other shells, see the other `activate.*` scripts in the `.env/bin/`
    directory. If you are on Windows, run
    ```sh
    .env\Scripts\activate.bat
    ```

4.  Now you can install all of the required packages using
    ```sh
    pip install -r requirements.txt
    ```

### Step 3: Running code via venv's python
From src directory run
```sh
python -m tempgen
```

### Step 4: Creating a Portable Executable

1.  Exit a virtual environment if in one (run `deactivate`).
2.  Install `pyinstaller` with
    ```sh
    pip3 install pyinstaller
    ```
3.  Enter the virtual environment (run `source .env/bin/activate` or OS/shell
    equivalent).
4.  Run the following command to create a binary file in src/tempgen/dist
    ```sh
    python package.py
    ```

### Step 4: Testing
This project uses pytest and mostly relies on snapshot testing. To trigger tests run
```sh
pytest
```
optionally with -vv and -s flags for verbosity and prints.

After each change that presumes expected generated output file changes one has to update snapshots by running
```sh
pytest --snapshot-update
```



[GitHub]: https://github.com/
[pyinstaller]: http://www.pyinstaller.org/
[pytest]: https://pytest.org/
[tox]: https://github.com/tox-dev/tox
[virtual environment]: https://docs.python.org/3/tutorial/venv.html
