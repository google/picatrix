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
"""Tests for the picatrix framework."""
from typing import Optional
from typing import Text

from picatrix.lib import framework
from picatrix.lib import manager
from picatrix.magics import common


def my_very_own_test_magic(data: Text, stuff: Optional[int] = 20) -> Text:
  """This is a magic that is used for testing.

    Args:
        data (str): This is a string.
        stuff (int): And this is a number.

    Returns:
        str: A string that combines the two parameters together.
  """
  return f'{data.strip()} - {stuff}'


def test_registration():
  """Test the magic decorator."""
  manager.MagicManager.clear_magics()
  _ = framework.picatrix_magic(my_very_own_test_magic)
  magic = framework.picatrix_magic(common.picatrixmagics)

  df = magic(line='')
  assert len(df) == 2
  assert set(df.columns) == set(manager.MagicManager.MAGICS_DF_COLUMNS)
  assert set(df.name.unique()) == set(
      ['my_very_own_test_magic', 'picatrixmagics'])

  magic = framework.picatrix_magic(common.last_output)
  same_df = magic(line='')
  assert same_df.equals(df)
