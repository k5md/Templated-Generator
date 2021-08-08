import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    os.path.join('src', '__main__.py'),
    '--name', 'TempGen',
    '--noconsole',
    '--clean',
    '--distpath', os.path.join('dist'),
    '--onedir',
    '--add-data', os.pathsep.join([os.path.join('src', 'locales'), 'locales']),
    '--noconfirm'
])