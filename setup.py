#!/usr/bin/env python

from distutils.core import setup


def long_description():
    with open('README') as f:
        return f.read()

setup(
    name='son',
    version='0.1',
    description='(SON) Simple Object Notation data interchange format.',
    long_description=long_description(),
    author='Aleksander Gurin',
    author_email='alek.gurin@gmail.com',
    url='https://github.com/aleksandergurin/simple-object-notation',
    py_modules=['son'],
    license='Public Domain',
    keywords='simple object notation, data format, serialization, deserialization',
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
