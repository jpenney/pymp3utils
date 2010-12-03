#!/usr/bin/env python
#
# setup.py for pymp3utils
from setuptools import setup, find_packages

setup(name='pymp3utils',
      version='0.1.0',
      author="Jason Penney",
      author_email="jpenney@jczorkmid.net",
      url="http://jasonpenney.net/",
      license="GPL",
      packages=find_packages(exclude=['test.*']),
      install_requires='''
      eyeD3 >= 0.6.17
      argparse
      MP3_Tools
      ''',
      entry_points="""
      [console_scripts]
      mp3sum = pymp3utils.mp3sum.console:main
      """,
      dependency_links = [
          'http://github.com/kirkeby/python-mp3/tarball/master#egg=MP3_Tools-0.1'
          ],
      include_package_data = True,
      exclude_package_data = {'': ['test/*']}
      )
