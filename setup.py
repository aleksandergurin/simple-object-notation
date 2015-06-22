#!/usr/bin/env python

import os
import sys

from distutils.core import setup, Command

# if sys.argv[-1] == 'publish':
#     os.system('python setup.py sdist upload')
#     os.system('python setup.py bdist_wheel upload')
#     sys.exit()
#
# class PyTest(Command):
#     user_options = []
#
#     def initialize_options(self):
#         pass
#
#     def finalize_options(self):
#         pass
#
#     def run(self):
#         import pytest
#         errno = pytest.main(["tests.py"])
#         sys.exit(errno)

def long_description():
    with open('README') as f:
        return f.read()

setup(
    name='son',
    version='0.1',
    description='Simple Object Notation data interchange format.',
    long_description=long_description(),
    author='Aleksander Gurin',
    author_email='alek.gurin@gmail.com',
    url='https://github.com/aleksandergurin/simple-object-notation',
    py_modules=['son'],
    license='Public Domain',
    keywords='simple object notation, data format, serialization, deserialization',
    # cmdclass={'test': PyTest},
    # test_suite='tests',
    # tests_require='pytest',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Public Domain',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development'
    ]
)