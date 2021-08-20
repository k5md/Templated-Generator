import os
import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

approot = os.getcwd()
with open(os.path.join(approot, 'src', 'tempgen', '__about__.py'), "r", encoding="utf-8") as file:
    about = file.read()
    exec(about)

setuptools.setup(
    name = __title__,
    version = __version__,
    author = __author__,
    author_email = __email__,
    description = __summary__,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = __uri__,
    project_urls = {
        "Bug Tracker": "https://github.com/k5md/Templated-Generator/issues",
    },
    license = __license__,
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: %s" % __license__,
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Topic :: Utilities",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
    ],
    package_dir = { '': 'src' },
    packages = setuptools.find_packages(where='src'),
    python_requires = ">=3.6",
    include_package_data = True,
)