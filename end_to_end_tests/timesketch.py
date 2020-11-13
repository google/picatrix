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


class TimesketchTest(interface.BaseEndToEndTest):
  """End to end tests for Timesketch magics functionality."""

  NAME = 'timesketch_test'

  def _setup_client(self, ip):
    """Setup the TimesketchAPI object into the IPython session."""
    ip.run_cell(raw_cell='from timesketch_api_client import client')
    _ = ip.run_cell(raw_cell=(
        '_client = client.TimesketchApi(\n'
        '    host_uri="https://demo.timesketch.org",\n'
        '    username="demo",\n'
        '    password="demo",\n'
        '    verify=True,\n'
        '    auth_mode="userpass")'))
    _ = ip.run_cell(raw_cell=(
        'from picatrix.lib import state\n'
        'state_obj = state.state()\n'
        'state_obj.add_to_cache(\'timesketch_client\', _client)\n'
    ))

  def test_get_sketch(self, ip: TerminalInteractiveShell):
    """Test fetching a sketch."""
    self._setup_client(ip)
    sketch = ip.run_cell('client.get_sketch(6)')
    self.assertions.assertEqual(sketch.id, 6)
    self.assertions.assertEqual(sketch.name, 'Szechuan Sauce - Challenge')


manager.EndToEndTestManager.register_test(TimesketchTest)
