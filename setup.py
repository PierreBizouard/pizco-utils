#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import sys
    reload(sys).setdefaultencoding("UTF-8")
except:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import codecs


def read(filename):
    return codecs.open(filename, encoding='utf-8').read()


long_description = '\n\n'.join([read('README'),
                                read('AUTHORS'),
                                read('CHANGES')])

__doc__ = long_description


requirements = []
if sys.version_info < (3, 2):
    requirements.append('futures')
if sys.version_info < (2, 7):
    requirements.append('unittest2')

setup(
    name='PizcoUtils',
    version='0.1.dev0',
    description='Python Utils remote objects with ZMQ',
    long_description=long_description,
    author='Pierre Bizouard',
    author_email='pierre.bizouard@gmail.com',
    url='https://github.com//PierreBizouard//pizcoutils',
    packages=['pizcoutils'],
    test_suite='pizcoutils.testsuite.testsuite',
    install_requires=requirements,
    package_data={},
    include_package_data = True,
    extras_require = {
        'pizco': ['pizco'],
        },
    license='BSD',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering',
      'Topic :: Software Development :: Libraries',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.0',
      'Programming Language :: Python :: 3.1',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
    ])
