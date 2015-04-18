#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='clarify_python',
    version='1.1.1',
    description='The Clarify Python 3 Helper Library wraps the entire Clarify API in Python 3.x function calls.',
    long_description=readme + '\n\n' + history,
    author='Paul Murphy',
    author_email='paul@clarify.io',
    url='https://github.com/Clarify/clarify_python',
    packages=[
        'clarify_python',
    ],
    package_dir={'clarify_python':
                 'clarify_python'},
    include_package_data=True,
    install_requires=[
         'urllib3',
         'certifi'
    ],
    license="MIT",
    zip_safe=False,
    keywords='clarify_python clarify',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 3",
    ],
    test_suite='tests',
)
