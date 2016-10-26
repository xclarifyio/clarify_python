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
    version='3.1.0',
    description='The Clarify Python Helper Library wraps the entire Clarify API in a Python 3.x / 2.7 Client class.',
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
    entry_points={
        'console_scripts': [
            'clarify_export = clarify_python.clarify_export:main'
        ]
    },
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
    tests_require=[
        # httpretty 0.8.11 breaks due to being unable to find / open
        # a requirements file
        # httpretty 0.8.12 breaks due to having invalid python3 lambda
        # syntax
        'httpretty<=0.8.10',
        'behave>=1.2.5'
    ],
    test_suite='tests',
)
