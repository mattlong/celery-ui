from __future__ import absolute_import

import sys
import os
import shutil
import sphinx.config

from celery_ui import quickstart
from celery_ui.utils import ensure_directory, delete_directory
from celery_ui.utils import copy_resource_dir

class MyConfig(sphinx.config.Config):
    def __init__(self, *args, **kwargs):
        super(MyConfig, self).__init__(*args, **kwargs)
        for ext in ['celery.contrib.sphinx', 'celery_ui.contrib.sphinx']:
            if ext not in self.extensions:
                self.extensions.append(ext)
sphinx.config.Config = MyConfig


def call_sphinx_apidoc(rootpath, opts):
    import sphinx.apidoc

    output_dir = os.path.join(opts.output_dir, '_apidoc')
    ensure_directory(output_dir)
    argv = [
        'sphinx-apidoc',
        '-e',
        '-o', output_dir,
        rootpath
    ]
    sphinx.apidoc.main(argv=argv)

    return output_dir


def call_sphinx_build(rootpath, opts):
    import sphinx

    output_dir = os.path.join(opts.output_dir, '_temp')
    ensure_directory(output_dir)

    # e.g. sphinx-build -b html -d build/doctrees   source build/html
    argv = [
        'sphinx-build',
        '-b', 'html',
    ]

    if opts.debug:
        argv.append('-v')

    argv.append(rootpath)  # source
    argv.append(output_dir)  # destination

    return_code = sphinx.build_main(argv=argv)

    if return_code != 0:
        raise Exception('Error running sphinx-build')

    return output_dir


def extract_generated_html(source_dir, opts):
    for filename in os.listdir(source_dir):
        if filename == 'celery_tasks.html':
            path = os.path.join(source_dir, filename)
            shutil.copy(path, opts.output_dir)


def main(argv=sys.argv):
    import optparse

    parser = optparse.OptionParser(usage="""\
usage: %prog [options] -o <output_path> -p <static_prefix> <module_path>

TODO: Write some sort of description here...""")

    parser.add_option('-p', '--prefix', dest='static_prefix',
                    help='Prefix to use in templates for links to static assets')
    parser.add_option('-o', '--output-dir', action='store', dest='output_dir',
                      help='Directory to place all output', default='')
    parser.add_option('-c', '--clean', action='store_true', dest='clean',
                      help='Clear output directory before building', default=False)
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='Debug mode; do not delete intermediate files', default=False)

    (opts, args) = parser.parse_args(argv[1:])

    if not args:
        parser.error('A package path is required')

    if not opts.output_dir:
        parser.error('An output directory is required.')

    rootpath = args[0]
    rootpath = os.path.normpath(os.path.abspath(rootpath))

    # specify env vars
    if opts.static_prefix is not None:
        os.environ['CELERY_UI_STATIC_PREFIX'] = opts.static_prefix

    # make sure the parent directory of the root package specified is on the path
    python_path = [os.path.abspath(p) for p in sys.path]
    parent_path = os.path.abspath(os.path.join(rootpath, '..'))
    if parent_path not in python_path:
        sys.path.insert(0, parent_path)

    ensure_directory(opts.output_dir, empty=opts.clean)

    temp_directories = []

    apidoc_source = call_sphinx_apidoc(rootpath, opts)
    temp_directories.append(apidoc_source)

    # generates conf.py, _templates, etc.
    quickstart.generate(apidoc_source)

    sphinx_output_dir = call_sphinx_build(apidoc_source, opts)
    temp_directories.append(sphinx_output_dir)

    # move generated .html files to final output location
    extract_generated_html(sphinx_output_dir, opts)

    # copy static assets to final output location
    static_dest = os.path.join(opts.output_dir, 'static')
    copy_resource_dir('static', static_dest)

    # cleanup
    if not opts.debug:
        for path in temp_directories:
            delete_directory(path)
