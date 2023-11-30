#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os

import setuptools
from setuptools import setup

PKG_NAME = 'ingen'
MAIN_PKG = 'ingen'
VERSION_PY_FILE = os.path.join(MAIN_PKG, 'version.py')
DEFAULT_PKG_VERSION = '1.0.0'
PKG_VERSION = DEFAULT_PKG_VERSION
PKG_VERSION_FILE = 'pkg_version.txt'

setup(name=PKG_NAME,
      version=PKG_VERSION,
      packages=setuptools.find_packages(include=['ingen', 'ingen.*']),
      package_data={},
      description='A Python script suite that generates interface files based on the given interface metadata/config '
                  'file',
      install_requires=open('requirements.txt').read().splitlines(),
      long_description="file: README.md, LICENSE.txt",
      classifiers=[
          'License :: Apache License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6'
      ],
      license='License :: Apache License',
      maintainer='Swarna Dhakad, Piyush Ranjan, Jatin Varlyani, Pooja Katariya',
      maintainer_email='swarna.dhakad@gmail.com, piyushranjan95@gmail.com, varlyanijatin88@gmail.com, '
                       'poojakatariya1811@gmail.com',
      url='https://github.com/blackrock/interface-generator')
