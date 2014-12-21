from __future__ import absolute_import
import os
import shutil
import errno
from pkg_resources import resource_filename


def ensure_directory(dir_path, empty=False):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    if empty:
        shutil.rmtree(dir_path)


def delete_directory(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


def copy_resource_dir(source_dir_name, dest_dir):
    ensure_directory(dest_dir)
    source_path = resource_filename(__name__, source_dir_name)
    for filename in os.listdir(source_path):
        src = os.path.join(source_path, filename)
        dest = os.path.join(dest_dir, filename)
        if not os.path.isfile(dest) or os.stat(src).st_mtime - os.stat(dest).st_mtime > 1:
            shutil.copy(src, dest)


def copy_resource_file(source_file_name, dest_dir):
    ensure_directory(dest_dir)
    source_path = resource_filename(__name__, source_file_name)
    shutil.copy(source_path, dest_dir)
