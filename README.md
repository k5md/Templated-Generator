# Templated generator

This template is used to create a Python package in a [virtual environment]
that can be tested with [tox].

## Virual Environments

This project runs in a _virtual environment_. A virtual environment is a
project specific Python installation that manages its own Python binaries and
packages. A major advantage that this offers is that each project has its own
environment that it runs in with no global configuration. This means that there
are no conflicts due to global package installation. Suppose one project uses
version `1.0.0` of a package and another project uses version `2.0.0` of
the same package, there are no issues because each project has its own version
of all of the package files.

See the [virtual environment] documentation for information on how this works.

## Using this Project

### Step 1: Install required programs

1.  Install Python 3
2.  Install `virtualenv`

    ```sh
    pip3 install virtualenv
    ```

### Step 2: Create a new project

1.  Copy this project somewhere and rename it to whatever your project will be
    called.
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
    virtualenv --python=/usr/bin/python3.5 .env
    ```

    instead.
3.  Assuming you are using the `bash` shell, run

    ```sh
    source .env/bin/activate
    ```

    For other shells, see the other `activate.*` scripts in the `.env/bin/`
    directory. If you are on Windows, use PowerShell and run

    ```sh
    .env\Scripts\activate.bat
    ```

You are now in a virtual environment. The `activate` script sets up some
environment variables and functions to point to a project local Python
configuration. This means that instead of using the the global `python` and
`pip` configuration, you are in the configuration contained in the `.env`
directory.

**Note**: The rest of this document assumes that the virtual environment is
active, unless otherwise noted.

You can see that you are in the virtual environment by running

```sh
# macOS/Linux
which python
# Windows
where python
```

and it will show `<path_to_project>/.env/bin/python` instead of the globally
installed Python, which will be something like `/usr/bin/python`. These paths
will be different on Windows.

If you ever want to leave the virtual environment, simply run `deactivate` in
the terminal.

**Note**: You need to activate the virtual environment every time you want to
work on the project in a new terminal.

**Note**: The virtual environment does not necessarily have to be activated to
use the configured environment. Instead or running `python` or `pip`, run
`.env/bin/python` or `.env/bin/pip`, respectively.

4.  Now you can install all of the required packages using

    ```sh
    pip install -r requirements.txt
    ```

You can see that these packages are installed in
`.env/lib/python3.7/site-packages`.

### Step 3: Running a binary

To use the binary, run

```sh
python3 src/tempgen
```

### Step 4: Creating a Portable Executable

Once the project is ready for production, an easy way to create an executable
is to use [pyinstaller].

1.  Exit a virtual environment if in one (run `deactivate`).
2.  Install `pyinstaller` with

    ```sh
    pip3 install pyinstaller
    ```

3.  Enter the virtual environment (run `source .env/bin/activate` or OS/shell
    equivalent).
4.  Run the following command to create a binary file in src/tempgen/dist

    ```sh
    python setup.py
    ```



[GitHub]: https://github.com/
[pyinstaller]: http://www.pyinstaller.org/
[pytest]: https://pytest.org/
[tox]: https://github.com/tox-dev/tox
[virtual environment]: https://docs.python.org/3/tutorial/venv.html
