from setuptools import setup, find_packages

VERSION_STRING = '0.0.3'

setup(
    name="celery-ui",
    packages=find_packages(),
    version = VERSION_STRING,
    author="Matt Long",
    license="MIT",
    author_email="matt@mattlong.org",
    url="https://github.com/mattlong/celery-ui",
    download_url = 'https://github.com/mattlong/celery-ui/tarball/' + VERSION_STRING,
    description="Execute Celery tasks through a web-based interface",
    install_requires=[
        'Celery>=3.1.17',
        'Sphinx>=1.2.3',
        'Werkzeug>=0.9.6',
        'docutils>=0.12',
    ],
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'celeryui-build = celery_ui.cmdline:main',
        ],
    },
    keywords = [],
    classifiers=[],
)
