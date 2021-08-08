import PyInstaller.__main__
import os
import shutil

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
archive_path = os.path.join(approot, 'TempGen.zip')

PyInstaller.__main__.run([
    entry,
    '--name', 'TempGen',
    '--noconsole',
    '--clean',
    '--distpath', dist_dir,
    '--onedir',
    *data_flat,
    '--noconfirm'
])

try:
    os.remove(archive_path)
except:
    pass

shutil.make_archive('TempGen', 'zip', os.path.join(dist_dir, 'TempGen'))