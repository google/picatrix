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

from setuptools import find_packages, setup

from picatrix import version


def from_file(name):
  """Read dependencies from requirements.txt file."""
  with open(name, "r", encoding="utf-8") as f:
    return f.read().splitlines()


long_description = (
    "picatrix - a framework to assist security analysts using "
    "Colab or Jupyter to perform forensic investigations.")

setup(
    name="picatrix",
    version=version.get_version(),
    description="Picatrix IPython Helpers",
    long_description=long_description,
    license="Apache License, Version 2.0",
    url="https://github.com/google/picatrix/",
    maintainer="Picatrix development team",
    maintainer_email="picatrix-developers@googlegroups.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=from_file("requirements.txt"),
    tests_require=from_file("requirements_dev.txt"),
    extras_require={
        "runtime": from_file("requirements_runtime.txt"),
    })
