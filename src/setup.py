from distutils.core import setup
import os, py2exe
import glob
import shutil

setup(
    options = {
      py2exe: {
        'includes': ['lxml._elementpath', 'tkinter', 'tkinter.filedialog', 'tkinter.font', 'tkinter.messagebox'],
        "bundle_files": 0
      }
    },
    windows = [{'script': '__main__.py'}],
)

dir_path = os.path.dirname(os.path.realpath(__file__))
shutil.copytree(os.path.join(dir_path, 'locales'), os.path.join(dir_path, 'dist', 'locales'))