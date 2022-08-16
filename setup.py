#!/usr/bin/env python3
#
#

import os
from setuptools import setup

setup(
    name='ttf2dxf',
    version='0.1.0',
    author='Oliver Dippel',
    author_email='o.dippel@gmx.de',
    packages=['ttf2dxf'],
    scripts=['bin/ttf2dxf'],
    url='https://github.com/multigcs/ttf2dxf/',
    license='LICENSE',
    description='simple python based ttf to dxf converter',
    long_description=open('README.md').read(),
    install_requires=['ezdxf', 'freetype-py'],
    include_package_data=True,
    data_files = []
)

