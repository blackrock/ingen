#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os

import setuptools
from setuptools import setup

PKG_NAME = 'ingen-lib'
MAIN_PKG = 'ingen'
VERSION_PY_FILE = os.path.join(MAIN_PKG, 'version.py')

setup(name=PKG_NAME,
      version='{{VERSION_PLACEHOLDER}}',
      packages=setuptools.find_packages(include=['ingen', 'ingen.*']),
      package_data={},
      description='A Python script suite that generates interface files based on the given interface metadata/config '
                  'file',
      install_requires=open('requirements.txt').read().splitlines(),
      long_description="InGen is a command line tool written on top of pandas and great_expectations to perform small "
                       "scale data transformations and validations without writing code. It is designed for "
                       "developers and analysts to quickly transform data by specifying their requirements in a "
                       "simple YAML file.",
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.12'
      ],
      license='License :: Apache License',
      maintainer='Swarna Dhakad, Piyush Ranjan, Jatin Varlyani, Pooja Katariya',
      maintainer_email='swarna.dhakad@gmail.com, piyushranjan95@gmail.com, varlyanijatin88@gmail.com, '
                       'poojakatariya1811@gmail.com',
      url='https://github.com/blackrock/interface-generator')
