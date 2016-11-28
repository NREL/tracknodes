#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from tracknodes import __version__, __author__

try:
    from setuptools import setup, find_packages
except ImportError:
    print("tracknodes needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

setup(
    name='tracknodes',
    version=__version__,
    description='Tracknodes keeps a history of node state and comment changes. Currently supports the Torque resource manager.',
    author=__author__,
    author_email='david.whiteside@nrel.gov',
    url='https://github.com/NREL/tracknodes',
    license='GPL',
    install_requires=["PyYAML"],
    package_dir={
        '': 'lib'},
    packages=find_packages('lib'),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    scripts=[
        'bin/tracknodes',
    ],
    data_files=[],
)
