import PyInstaller.__main__
import os
import shutil
import platform
import contextlib
from src.tempgen.__about__ import (
    __version__,
    __title__,
)

project_name = __title__
approot = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(approot, 'src', 'tempgen')
build_dir = os.path.join(approot, 'build')
dist_dir = os.path.join(approot, 'dist')
entry = os.path.join(src_dir, '__main__.py')
data = [
    (os.path.join(src_dir, 'locales'), os.sep.join([project_name, 'locales']))
]
data_zipped = [ ('--add-data', os.pathsep.join(entry)) for entry in data ] # https://pyinstaller.readthedocs.io/en/stable/spec-files.html#adding-data-files
data_flat = [item for sublist in data_zipped for item in sublist]

PyInstaller.__main__.run([
    entry,
    '--name', project_name,
    '--clean',
    '--distpath', dist_dir,
    '--onedir',
    *data_flat,
    '--noconfirm',
])

artifact_dir = os.path.join(approot, 'artifacts')
archive_name = '_'.join([project_name, platform.system(), __version__])
archive_file = '%s.zip' % archive_name
archive_path = os.path.join(artifact_dir, archive_file)
archive_path_temp = os.path.join(approot, archive_file)

if not os.path.exists(artifact_dir): os.mkdir(artifact_dir)
if os.path.exists(archive_path): os.remove(archive_path)
if os.path.exists(archive_path_temp): os.remove(archive_path_temp)

shutil.make_archive(archive_name, 'zip', os.path.join(dist_dir, project_name))
shutil.move(os.path.join(approot, archive_file), artifact_dir)
