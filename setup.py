#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import os
import re
import sys

from setuptools import find_packages
from setuptools import setup

def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

install_requires = [
    'requests',
    'docker'
]

setup(
    name='docker-parse',
    version=find_version("docker_parse", "__init__.py"),
    description='Parse docker-run options from a running Docker container',
    url='https://github.com/iamfat/docker-parse',
    author="Jia Huang",
    author_email="iamfat@gmail.com",
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='docker parse run options',
    packages=find_packages(exclude=['tests.*', 'tests']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'docker-parse=docker_parse:main',
        ],
    },
)
