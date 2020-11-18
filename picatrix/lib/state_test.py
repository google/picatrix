# -*- coding: utf-8 -*-
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
"""Tests for the pixatrix state object."""
from picatrix.lib import testlib


def test_getting_last_magic():
  """Test running a magic."""
  ip = testlib.InteractiveTest.get_shell()
  ip.run_cell(raw_cell='from picatrix.magics import common')
  res = ip.run_cell(raw_cell='common.picatrixmagics("")')
  output_df = res.result
  #output_df = ip.run_line_magic(magic_name='picatrixmagics', line='')

  code = (
      'df = common.last_output("")\n'
      'names = list(df.name.unique())\n'
      'sorted(names)')

  names = list(output_df['name'].unique())
  testlib.InteractiveTest.run_and_compare(code, expected_return=sorted(names))


def test_working_with_cache():
  """Test working with the cache."""
  ip = testlib.InteractiveTest.get_shell()
  res = ip.run_cell(raw_cell=(
      'from picatrix.lib import state\n'
      'state.state()\n'))
  assert res.success
  state_obj = res.result
  state_obj.add_to_cache('foobar', 1234)

  assert state_obj.get_from_cache('foobar') == 1234

  res = ip.run_cell(raw_cell=(
      'state_obj = state.state()\n'
      'state_obj.get_from_cache("foobar")\n'))
  assert res.success
  assert res.result == 1234

  res = ip.run_cell(raw_cell='state_obj.remove_from_cache("foobar")')
  assert res.success

  res = ip.run_cell(raw_cell='state_obj.get_from_cache("foobar")')
  assert res.success
  assert res.result is None
