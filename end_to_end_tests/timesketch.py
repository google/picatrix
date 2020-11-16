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

from timesketch_api_client import sketch

from . import interface
from . import manager


class TimesketchTest(interface.BaseEndToEndTest):
  """End to end tests for Timesketch magics functionality."""

  NAME = 'timesketch_test'

  def _setup_client(self, ip: TerminalInteractiveShell):
    """Setup the TimesketchAPI object into the IPython session."""
    ip.run_cell(raw_cell='from timesketch_api_client import client')
    res = ip.run_cell(raw_cell=(
        '_client = client.TimesketchApi(\n'
        '    host_uri="https://demo.timesketch.org",\n'
        '    username="demo",\n'
        '    password="demo",\n'
        '    verify=True,\n'
        '    auth_mode="userpass")'))
    self.assertions.assertTrue(res.success)
    res = ip.run_cell(raw_cell=(
        'from picatrix.lib import state\n'
        'state_obj = state.state()\n'
        'state_obj.add_to_cache(\'timesketch_client\', _client)\n'
    ))
    self.assertions.assertTrue(res.success)

  def _get_sketch(self, ip: TerminalInteractiveShell) -> sketch.Sketch:
    """Return a sketch object."""
    self._setup_client(ip)
    ip.run_line_magic(magic_name='timesketch_set_active_sketch', line='6')
    return ip.run_line_magic(magic_name='timesketch_get_sketch', line='')

  def test_get_sketch(self, ip: TerminalInteractiveShell):
    """Test fetching a sketch."""
    sketch_obj = self._get_sketch(ip)
    self.assertions.assertEqual(sketch_obj.id, 6)
    self.assertions.assertEqual(sketch_obj.name, 'Szechuan Sauce - Challenge')

  def test_list_views(self, ip: TerminalInteractiveShell):
    """Test listing up the available views for a sketch."""
    _ = self._get_sketch(ip)
    views = ip.run_line_magic(magic_name='timesketch_list_views', line='')
    expected_views = set([
        '18:Szechuan Hits',
        '19:Szechuan All Hits',
        '16:email_addresses'])
    self.assertions.assertEqual(set(views.keys()), expected_views)

  def test_query_data(self, ip: TerminalInteractiveShell):
    """Test querying for data in a sketch."""
    _ = self._get_sketch(ip)
    df = ip.run_line_magic(
        magic_name='timesketch_query', line=(
            '--fields datetime,origin,message,hostname,name secret AND '
            'data_type:"windows:shell_item:file_entry"'))
    df_slice = df[df.origin == 'Beth_Secret.lnk']
    self.assertions.assertTrue(df_slice.shape[0] > 0)
    origin_set = set(df.origin.unique())
    expected_set = set([
        '9b9cdc69c1c24e2b.automaticDestinations-ms', 'Beth_Secret.lnk',
        'HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software'
        '\\Microsoft\\Windows\\Shell\\BagMRU\\0\\0\\0',
        'NoJerry.lnk', 'PortalGunPlans.lnk', 'SECRET_beth.lnk', 'Secret.lnk',
        'Szechuan Sauce.lnk', 'f01b4d95cf55d32a.automaticDestinations-ms'])

    self.assertions.assertSetEqual(origin_set, expected_set)

  def test_context_date(self, ip: TerminalInteractiveShell):
    """Test querying for contex surrounding a date."""
    _ = self._get_sketch(ip)
    df = ip.run_line_magic(
        magic_name='timesketch_context_date', line=(
            '--minutes 10 --fields datetime,message,data_type,event_identifier'
            ',username,workstation 2020-09-18T22:24:36'))

    self.assertions.assertTrue(df.shape[0] > 5000)
    logon_df = df[df.event_identifier == 4624]
    logged_in_users = list(logon_df.username.unique())
    self.assertions.assertTrue('Administrator' in logged_in_users)
    self.assertions.assertTrue('DWM-1' in logged_in_users)

    df.sort_values('datetime', inplace=True)
    first_series = df.iloc[0]
    last_series = df.iloc[-1]

    first_time = first_series.datetime
    last_time = last_series.datetime
    delta = last_time - first_time
    delta_rounded = delta.round('min')

    # This should be 10 minutes or 600 seconds.
    self.assertions.assertTrue(delta_rounded.total_seconds() == 600.0)


manager.EndToEndTestManager.register_test(TimesketchTest)
