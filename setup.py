#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# setup.py for pymp3utils

from setuptools import setup, find_packages
import os.path
import sys

_pkgname = 'pymp3utils'


def get_version():
    ver='unknown'
    if os.path.exists(_pkgname):
        sys.path.insert(0, '.')
        from pymp3utils._version import __version__ as pkg_version
        ver = pkg_version
        sys.path = sys.path[1:]
    return ver

setup(
    name=_pkgname,
    version=get_version(),
    author='Jason Penney',
    author_email='jpenney@jczorkmid.net',
    url='http://jasonpenney.net/',
    license='GPL',
    packages=find_packages(exclude=['test.*']),
    install_requires='''
      eyeD3 >= 0.6.17
      mutagen >= 1.20
      argparse
      MP3_Tools
      ''',
    entry_points="""
      [console_scripts]
      mp3sum = pymp3utils.mp3sum.console:main
      mp3gainer = pymp3utils.mp3gain.console:main
      """,
    dependency_links=['http://github.com/kirkeby/python-mp3/tarball/mas'
                      'ter#egg=MP3_Tools-0.1'],
    include_package_data=True,
    exclude_package_data={'': ['test/*']},
    )
