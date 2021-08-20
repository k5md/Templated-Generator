import PyInstaller.__main__
import os
import shutil
import platform
from src.__about__ import (
    __version__,
    __title__,
)

project_name = __title__
approot = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(approot, 'src')
build_dir = os.path.join(approot, 'build')
dist_dir = os.path.join(approot, 'dist')
entry = os.path.join(src_dir, '__main__.py')
data = [
    (os.path.join(src_dir, 'locales'), 'locales')
]
data_zipped = [ ('--add-data', os.pathsep.join(entry)) for entry in data ] # https://pyinstaller.readthedocs.io/en/stable/spec-files.html#adding-data-files
data_flat = [item for sublist in data_zipped for item in sublist]

PyInstaller.__main__.run([
    entry,
    '--name', project_name,
    '--noconsole',
    '--clean',
    '--distpath', dist_dir,
    '--onedir',
    *data_flat,
    '--noconfirm'
])

artifact_dir = os.path.join(approot, 'artifacts')
archive_name = '_'.join([project_name, platform.system(), __version__])

try:
    os.mkdir(artifact_dir)
except FileExistsError:
    pass

shutil.make_archive(archive_name, 'zip', os.path.join(dist_dir, project_name))
shutil.move(os.path.join(approot, archive_name + '.zip'), artifact_dir)
