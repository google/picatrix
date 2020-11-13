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

  def _get_sketch(self, ip):
    """Return a sketch object."""
    self._setup_client(ip)
    ip.run_line_magic(magic_name='timesketch_set_active_sketch', line='6')
    return ip.run_line_magic(magic_name='timesketch_get_sketch', line='')

  def test_get_sketch(self, ip: TerminalInteractiveShell):
    """Test fetching a sketch."""
    sketch = self._get_sketch(ip)
    self.assertions.assertEqual(sketch.id, 6)
    self.assertions.assertEqual(sketch.name, 'Szechuan Sauce - Challenge')

  def test_query(self, ip: TerminalInteractiveShell):
    """Test fetching a sketch."""
    _ = self._get_sketch(ip)
    views = ip.run_line_magic(magic_name='timesketch_list_views', line='')
    expected_views = set([
        '18:Szechuan Hits',
        '19:Szechuan All Hits',
        '16:email_addresses'])
    self.assertions.assertEqual(set(views.keys()), expected_views)




manager.EndToEndTestManager.register_test(TimesketchTest)
