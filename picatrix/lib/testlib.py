# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test library for picatrix."""
from typing import Any
from typing import Text

from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.testing.globalipapp import start_ipython

from picatrix.lib import manager


manager.MagicManager.is_test = True


class InteractiveTest:
  """Class that helps with interactive tests for picatrix."""

  _shell: TerminalInteractiveShell = None

  @classmethod
  def _init_shell(cls):
    """Initialize the shell."""
    ip = start_ipython()

    ip.run_cell(raw_cell='from picatrix import notebook_init')
    ip.run_cell(raw_cell='notebook_init.init()')
    cls._shell = ip

  @classmethod
  def get_shell(cls) -> TerminalInteractiveShell:
    """Return an interactive shell, initializing it for the first time."""
    if cls._shell:
      return cls._shell
    cls._init_shell()
    return cls._shell

  @classmethod
  def run_and_compare(cls, code: Text, expected_return: Any):
    """Run code in shell, get returns and assert against expected returns."""
    shell = cls.get_shell()
    res = shell.run_cell(raw_cell=code)
    assert res.success
    assert res.result == expected_return
