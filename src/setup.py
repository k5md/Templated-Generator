from distutils.core import setup
import py2exe, sys, os, decimal, json, tkinter.filedialog, tkinter.font, tkinter.messagebox, tkinter as tk, scrollableFrame, re, num2t4ru, datetime, i18n, parsers.docx, parsers.xlsx
import lxml._elementpath
import glob
import shutil

def find_data_files(source,target,patterns):
  if glob.has_magic(source) or glob.has_magic(target):
    raise ValueError("Magic not allowed in src, target")
  ret = {}
  for pattern in patterns:
    pattern = os.path.join(source,pattern)
    for filename in glob.glob(pattern):
      if os.path.isfile(filename):
          targetpath = os.path.join(target,os.path.relpath(filename,source))
          path = os.path.dirname(targetpath)
          ret.setdefault(path,[]).append(filename)
  return sorted(ret.items())

setup(
    options = {
      py2exe: {
        'includes': ['lxml._elementpath'],
        #'data_files': find_data_files('locales','',[ 'locales/*']), # does not work
      }
    },
    windows = [{'script': '__main__.py'}],
)

dir_path = os.path.dirname(os.path.realpath(__file__))
shutil.copytree(os.path.join(dir_path, 'locales'), os.path.join(dir_path, 'dist', 'locales'))