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
"""End to end tests of common picatrix magics."""

from IPython.terminal.interactiveshell import TerminalInteractiveShell

from . import interface
from . import manager


MAGIC_DEFINITION = (
    'from typing import Optional\n'
    'from typing import Text\n'
    '\n'
    'from picatrix.lib import framework\n'
    '\n'
    '@framework.picatrix_magic\n'
    'def my_silly_magic(data: Text, magnitude: Optional[int] = 100) -> Text:\n'
    '  """Return a silly string with no meaningful value.\n'
    '\n'
    '  Args:\n'
    '    data (str): This is a string that will be printed back.\n'
    '    magnitude (int): A number that will be displayed in the string.\n'
    '\n'
    '  Returns:\n'
    '    A string that basically combines the two options.\n'
    '  """\n'
    '  return f"This magical magic produced {magnitude} magics of '
    '{data.strip()}"\n')


class BasicTest(interface.BaseEndToEndTest):
  """End to end tests for query functionality."""

  NAME = 'basic_test'

  def test_picatrixmagics(self, ip: TerminalInteractiveShell):
    """Test the picatrixmagics."""
    magics = ip.run_line_magic(magic_name='picatrixmagics', line='')

    self.assertions.assertFalse(magics.empty)
    self.assertions.assertTrue(magics.shape[0] > 10)

  def test_magic_registration(self, ip: TerminalInteractiveShell):
    """Test registering a magic."""
    res = ip.run_cell(raw_cell=MAGIC_DEFINITION)
    self.assertions.assertTrue(res.success)

    magics = ip.run_line_magic(magic_name='picatrixmagics', line='')
    self.assertions.assertFalse(
        magics[magics.name == 'my_silly_magic'].empty)

    line = ip.run_line_magic(
        magic_name='my_silly_magic', line='--magnitude 23 this is my string')

    expected_return = (
        'This magical magic produced 23 magics of this is my string')
    self.assertions.assertEqual(line, expected_return)

manager.EndToEndTestManager.register_test(BasicTest)
