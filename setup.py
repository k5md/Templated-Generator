import os
import setuptools

approot = os.getcwd()

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

with open(os.path.join(approot, "src", "tempgen", "__about__.py"), "r", encoding="utf-8") as file:
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
    package_dir = { "": "src" },
    packages = setuptools.find_packages(
        where="src",
        include=["tempgen*"],
        exclude=["tempgen_*"]),
    python_requires = ">=3.7",
    install_requires=[
        "odfpy>=1.4.1",
        "python-docx>=0.8.11",
        "python-i18n>=0.3.9",
        "python-i18n[YAML]",
    ],
    include_package_data = True,
)
