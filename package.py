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
src_dir = os.path.join(approot, 'src')
build_dir = os.path.join(approot, 'build')
dist_dir = os.path.join(approot, 'dist')

"""
    NOTE: to understand reasons of nultiple ugly builds being present instead of one,
    check 7 y.o issues with pyinstaller multi-executable builds support, starting from
    https://github.com/pyinstaller/pyinstaller/issues/167
"""

gui_name = '%s_gui' % project_name
cli_name = '%s_cli' % project_name

gui_data = [
    (os.path.join(src_dir, gui_name,'locales'), os.sep.join(['locales']))
]
gui_data_zipped = [ ('--add-data', os.pathsep.join(entry)) for entry in gui_data ] # https://pyinstaller.readthedocs.io/en/stable/spec-files.html#adding-data-files
gui_data_flat = [item for sublist in gui_data_zipped for item in sublist]

builds = [
    {
        'entry': os.path.join(src_dir, cli_name, '__main__.py'),
        'name': '%s_cli' % project_name,
        'console': '--console',
    },
    {
        'entry': os.path.join(src_dir, gui_name, '__main__.py'),
        'name': gui_name,
        'data': gui_data_flat,
        'console': '--noconsole',
    }
]

for build in builds:
    arguments = [
        build['entry'],
        '--name', build['name'],
        build['console'],
        '--onedir',
        '--distpath', dist_dir,
        '--clean',
        '--noconfirm',
    ]
    if 'data' in build: arguments += build['data']

    PyInstaller.__main__.run(arguments)

    artifact_dir = os.path.join(approot, 'artifacts')
    archive_name = '_'.join([build['name'], platform.system(), __version__]).lower()
    archive_file = '%s.zip' % archive_name
    archive_path = os.path.join(artifact_dir, archive_file)
    archive_path_temp = os.path.join(approot, archive_file)

    if not os.path.exists(artifact_dir): os.mkdir(artifact_dir)
    if os.path.exists(archive_path): os.remove(archive_path)
    if os.path.exists(archive_path_temp): os.remove(archive_path_temp)

    shutil.make_archive(archive_name, 'zip', os.path.join(dist_dir, build['name']))
    shutil.move(os.path.join(approot, archive_file), artifact_dir)
