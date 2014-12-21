from __future__ import absolute_import
import os
import time
from io import open
from docutils.utils import column_width

from celery_ui.utils import copy_resource_file, copy_resource_dir


# based on sphinx.quickstart
def generate(rootpath, overwrite=False, silent=False):
    def write_file(fpath, content, newline=None):
        if overwrite or not os.path.isfile(fpath):
            print 'Creating file %s.' % fpath
            f = open(fpath, 'wt', encoding='utf-8', newline=newline)
            try:
                f.write(content)
            finally:
                f.close()
        else:
            print 'File %s already exists, skipping.' % fpath

    # copy template to within sphinx build directory
    template_dest = os.path.join(rootpath, '_templates')
    copy_resource_dir('templates', template_dest)

    copy_resource_file('modules/conf.py', rootpath)

    project_name = 'celery-ui'
    masterfile = os.path.join(rootpath, 'index.rst')

    mastertoctree = ''
    for module in ['modules']:
        mastertoctree += '   %s\n' % module

    d = {
        'project': project_name,
        'now': time.asctime(),
        'project_underline': column_width(project_name) * '=',
        'mastertocmaxdepth': 4,
        'mastertoctree': mastertoctree,
    }
    write_file(masterfile, MASTER_FILE % d)


MASTER_FILE = u'''\
.. %(project)s documentation master file, created by
   sphinx-quickstart on %(now)s.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to %(project)s's documentation!
===========%(project_underline)s=================

Contents:

.. toctree::
   :maxdepth: %(mastertocmaxdepth)s

%(mastertoctree)s
'''
