import setuptools
from src.__about__ import (
    __author__,
    __email__,
    __license__,
    __summary__,
    __title__,
    __uri__,
    __version__,
)

with open("README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=__summary__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__uri__,
    project_urls={
        "Bug Tracker": "https://github.com/k5md/Templated-Generator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: %s" % __license__,
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Topic :: Utilities",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
    ],
    package_dir={"": "tempgen"},
    packages=setuptools.find_packages(where="tempgen"),
    python_requires=">=3.6",
)