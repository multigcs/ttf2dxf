#!/usr/bin/env python3
#
#

import os
from setuptools import setup

setup(
    name='dxfbox',
    version='0.1.0',
    author='Oliver Dippel',
    author_email='o.dippel@gmx.de',
    packages=['dxfbox'],
    scripts=['bin/dxfbox'],
    url='https://github.com/multigcs/dxfbox/',
    license='LICENSE',
    description='simple python based dxf box generator',
    long_description=open('README.md').read(),
    install_requires=['ezdxf'],
    include_package_data=True,
    data_files = []
)

