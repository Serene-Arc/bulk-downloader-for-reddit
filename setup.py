#!/usr/bin/env python3
# encoding=utf-8

from setuptools import setup

setup(setup_requires=['pbr', 'appdirs'], pbr=True, data_files=[('config', ['bdfr/default_config.cfg'])], python_requires='>=3.9.0')
