#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os

import setuptools
from setuptools import setup

PKG_NAME = 'ingen-lib'
MAIN_PKG = 'ingen'
VERSION_PY_FILE = os.path.join(MAIN_PKG, 'version.py')


def read_requirements():
    """Parse requirements.txt for install_requires, ignoring blank lines and comments.

    The previous ``open(...).read().splitlines()`` passed every line through verbatim, so any
    comment or blank line became an invalid requirement. This makes the manifest safely
    annotatable (e.g. documenting why a version is pinned).
    """
    with open('requirements.txt') as fh:
        lines = [line.strip() for line in fh]
    return [line for line in lines if line and not line.startswith('#')]


def resolve_version():
    """Resolve the package version.

    At release time the CI workflow (.github/workflows/python-publish.yml) replaces the
    ``{{VERSION_PLACEHOLDER}}`` token below with the git tag via ``sed``. For local/editable
    installs the token is left intact, which is NOT a valid PEP 440 version and breaks
    ``pip install -e .``. So when the token has not been substituted, fall back to a valid
    development version. The literal token is preserved verbatim so the existing CI ``sed`` keeps
    working unchanged.
    """
    version = '{{VERSION_PLACEHOLDER}}'
    if version.startswith('{{'):
        return '0.0.0.dev0'
    return version


setup(name=PKG_NAME,
      version=resolve_version(),
      # Upper bound is real, not arbitrary: InGen uses the legacy great_expectations API, which
      # requires numpy<2. numpy<2 only ships wheels through CPython 3.12, so on 3.13+ pip would try
      # to build numpy from source (needs a C compiler). Capping here makes pip reject 3.13+ with a
      # clear "Requires-Python" message instead of a confusing build failure.
      python_requires='>=3.9,<3.13',
      packages=setuptools.find_packages(include=['ingen', 'ingen.*']),
      package_data={},
      description='A Python script suite that generates interface files based on the given interface metadata/config '
                  'file',
      install_requires=read_requirements(),
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
