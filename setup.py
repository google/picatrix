#!/usr/bin/env python
# Copyright 2020 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This is the setup file for the project."""
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup

from picatrix import version


def parse_requirements(filename):
  """Parse python requirements.

  Args:
    filename (str): The requirement file to read.

  Returns:
    List[str]: a list of requirements.
  """
  with open(filename) as requirements:
    # Skipping -i https://pypi.org/simple
    return requirements.readlines()[1:]


setup(
    name='picatrix',
    version=version.get_version(),
    description='Picatrix IPython Helpers',
    license='Apache License, Version 2.0',
    url='https://github.com/google/picatrix/',
    maintainer='Picatrix development team',
    maintainer_email='picatrix-developers@googlegroups.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_requirements('requirements.txt'),
)
