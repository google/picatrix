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

from timesketch_api_client import client

from . import interface
from . import manager


class TimesketchTest(interface.BaseEndToEndTest):
  """End to end tests for Timesketch magics functionality."""

  NAME = 'timesketch_test'

  _client: client.TimesketchApi = None

  def _get_client(self) -> client.TimesketchApi:
    """Returns a TimesketchApi client object."""
    if self._client:
      return self._client

    self._client = client.TimesketchApi(
        host_uri='https://demo.timesketch.org',
        username='demo',
        password='demo',
        verify=True,
        auth_mode='userpass')
    return self._client

  def _setup(self, ip, sketch_id=0):
    """Setup the test."""
    client = self._get_client()
    _ = ip.run_cell(raw_cell=(
        'from picatrix.lib import state\n'
        'state_obj = state.state()\n'
        'state_obj.add_to_cache(\'timesketch_client\', client)\n'
    ))
    if sketch_id:
      _ = ip.run_cell(raw_cell=(
          f'sketch = client.get_sketch({sketch_id})\n'
          f'state_obj.add_to_cache(\'timesketch_sketch\', sketch)\n'))

  def test_get_sketch(self, ip: TerminalInteractiveShell):
    """Test fetching a sketch."""
    self._setup(ip)
    sketch = ip.run_cell('client.get_sketch(6)')
    self.assertions.assertEquals(sketch.id, 6)
    self.assertions.assertEquals(sketch.name, 'Szechuan Sauce - Challenge')


manager.EndToEndTestManager.register_test(TimesketchTest)
