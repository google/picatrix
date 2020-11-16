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
"""Interface for end-to-end tests."""

from typing import Callable
from typing import Generator
from typing import Text
from typing import Tuple

import unittest
import inspect
import collections
import logging

from IPython.terminal.interactiveshell import TerminalInteractiveShell


logger = logging.getLogger('picatrix.e2e_test')

# Default values based on Docker config.
TEST_DATA_DIR = '/usr/local/src/picatrix/end_to_end_tests/test_data'


class BaseEndToEndTest:
  """Base class for end to end tests.

  Attributes:
      assertions: Instance of unittest.TestCase
  """
  assertions: unittest.TestCase

  NAME = 'name'

  def __init__(self):
    """Initialize the end-to-end test object."""
    self.assertions = unittest.TestCase()
    self._counter = collections.Counter()

  def _get_test_methods(self) -> Generator[
      Tuple[Text, Callable[[TerminalInteractiveShell], None]], None, None]:
    """Inspect class and list all methods that matches the criteria.

    Yields:
        Function name and bound method.
    """
    for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
      if name.startswith('test_'):
        yield name, func

  def setup(self):
    """Setup function that is run before any tests.

    This is a good place to import any data that is needed.
    """

  def run_tests(self, ip: TerminalInteractiveShell) -> collections.Counter:
    """Run all test functions from the class.

    Returns:
        Counter of number of tests and errors.
    """
    logger.info('*** %s ***', self.NAME)
    for test_name, test_func in self._get_test_methods():
      self._counter['tests'] += 1
      logger.info('Running test: %s ...', test_name)
      try:
        test_func(ip)
      except Exception:  # pylint: disable=broad-except
        logger.error(
            'Error while running test %s', self.NAME, exc_info=True)
        self._counter['errors'] += 1
        continue
      logger.info('%s [OK]', test_name)
    return self._counter
