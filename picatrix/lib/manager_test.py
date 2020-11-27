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
"""Tests for the pixatrix manager."""
import typing

import pytest
import mock

from picatrix.lib import manager
from picatrix.lib import utils


manager.get_ipython = mock.MagicMock()
utils.get_ipython = mock.MagicMock()


def test_registration():
  """Test registering a magic and getting a copy of it and de-registering."""
  manager.MagicManager.clear_magics()

  def my_magic(cell=None, line=None):
    """This is a magic."""
    if not cell:
      cell = 'foo'
    if not line:
      line = 'bar'
    return f'{cell}{line}'

  my_magic.magic_name = 'magical_function'
  my_magic.fn = my_magic
  manager.MagicManager.register_magic(my_magic)

  magic_from_manager = manager.MagicManager.get_magic('magical_function')
  assert magic_from_manager() == 'foobar'

  my_magic.magic_name = 'other_magic'
  def conditional():
    return False

  manager.MagicManager.register_magic(my_magic, conditional=conditional)
  magic_from_manager = manager.MagicManager.get_magic('other_magic')
  assert magic_from_manager is None

  manager.MagicManager.register_magic(my_magic)
  magic_from_manager = manager.MagicManager.get_magic('other_magic')
  assert magic_from_manager() == 'foobar'

  manager.MagicManager.deregister_magic('other_magic')
  magic_from_manager = manager.MagicManager.get_magic('other_magic')
  assert magic_from_manager is None

  manager.MagicManager.deregister_magic('magical_function')
  magic_from_manager = manager.MagicManager.get_magic('magical_function')
  assert magic_from_manager is None

  with pytest.raises(KeyError):
    manager.MagicManager.deregister_magic('does_not_exist')


def test_magic_info():
  """Test the get_magic_info."""
  # Start by clearing the current registration.
  manager.MagicManager.clear_magics()
  def magical_func():
    """This is a magical function that returns pure magic."""
    return 'magic'

  magical_func.magic_name = 'magical_function'
  magical_func.fn = magical_func
  manager.MagicManager.register_magic(magical_func)

  def second_magic():
    """This is even more magic."""
    return 'fab'
  second_magic.magic_name = 'some_magic'
  second_magic.fn = second_magic
  manager.MagicManager.register_magic(second_magic)

  def other_magic():
    """Could this be it?"""
    return 'true magic'

  other_magic.magic_name = 'other_magic'
  other_magic.fn = other_magic
  manager.MagicManager.register_magic(other_magic)

  info_df = manager.MagicManager.get_magic_info(as_pandas=True)
  assert len(info_df) == 3
  assert not info_df[info_df.name == 'other_magic'].empty

  desc_set = set(info_df.description.unique())
  expected_set = set([
      'Could this be it?', 'This is even more magic.',
      'This is a magical function that returns pure magic.'])

  assert desc_set == expected_set

  entries = manager.MagicManager.get_magic_info(as_pandas=False)
  assert len(entries) == 3
  names = [x[0] for  x in entries]
  assert 'other_magic' in names
  assert 'some_magic' in names


def test_helper_registration():
  """Test registering helpers."""
  def helper_func(stuff: typing.Text):
    """This is a helper function that helps."""
    back = f'{stuff}'*3
    return f'{back}\n\nwasn\'t this helpful?'

  helper_dict = typing.get_type_hints(helper_func)
  manager.MagicManager.register_helper(
      name='helper_func', helper=helper_func,
      typing_help=helper_dict)

  df = manager.MagicManager.get_helper_info()
  assert not df[df.name == 'helper_func'].empty
  series = df.set_index('name').loc['helper_func']
  assert series.arguments == 'stuff [str]'
