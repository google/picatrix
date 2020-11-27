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
"""Class that defines the manager for all magics."""

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Text
from typing import Tuple
from typing import Union

from dataclasses import dataclass
import functools
import pandas
from IPython import get_ipython

from picatrix.lib import utils
from picatrix.lib import state


@dataclass
class Helper:
  """Small structure for a helper."""
  function: Callable[..., Any]
  help: Text
  types: Dict[Text, Any]


class MagicManager:
  """Manager class for Picatrix magics."""

  MAGICS_DF_COLUMNS = ['name', 'description', 'line', 'cell', 'function']

  _magics: Dict[Text, Callable[[Text, Text], Text]] = {}
  _helpers: Dict[Text, Helper] = {}

  @classmethod
  def clear_helpers(cls):
    """Clear all helper registration."""
    for helper_name in cls._helpers:
      try:
        utils.ipython_remove_global(helper_name)
      except KeyError:
        pass
    cls._helpers = {}

  @classmethod
  def clear_magics(cls):
    """Clear all magic registration."""
    magics = list(cls._magics.keys())
    for magic_name in magics:
      cls.deregister_magic(magic_name)

  @classmethod
  def deregister_helper(cls, helper_name: Text):
    """Remove a helper from the registration.

    Args:
      helper_name (str): the name of the helper to remove.

    Raises:
      KeyError: if the helper is not registered.
    """
    if helper_name not in cls._helpers:
      raise KeyError(f'Helper [{helper_name}] is not registered.')

    _ = cls._helpers.pop(helper_name)
    try:
      utils.ipython_remove_global(helper_name)
    except KeyError:
      pass

  @classmethod
  def deregister_magic(cls, magic_name: Text):
    """Removes a magic from the registration.

    Args:
      magic_name (str): the name of the magic to remove.

    Raises:
      KeyError: if the magic is not registered.
    """
    if magic_name not in cls._magics:
      raise KeyError(f'Magic [{magic_name}] is not registered.')

    _ = cls._magics.pop(magic_name)
    try:
      utils.ipython_remove_global(f'{magic_name}_func')
    except KeyError:
      pass

    # Attempt to remove the magic definition.
    ip = get_ipython()
    magics_manager = ip.magics_manager

    if not hasattr(magics_manager, 'magics'):
      return

    line_magics = magics_manager.magics.get('line', {})
    if magic_name in line_magics:
      _ = magics_manager.magics.get('line').pop(magic_name)

    cell_magics = magics_manager.magics.get('cell', {})
    if magic_name in cell_magics:
      _ = magics_manager.magics.get('cell').pop(magic_name)

  @classmethod
  def get_helper(cls, helper_name: Text) -> Optional[Callable[..., Any]]:
    """Return a helper function from the registration."""
    return cls._magics.get(helper_name)

  @classmethod
  def get_magic(cls, magic_name: Text) -> Callable[[Text, Text], Text]:
    """Return a magic function from the registration."""
    return cls._magics.get(magic_name)

  @classmethod
  def get_helper_info(cls, as_pandas: Optional[bool] = True) -> Union[
      pandas.DataFrame, List[Tuple[Text, Text]]]:
    """Get a list of all the registered helpers.

    Args:
      as_pandas (bool): boolean to determine whether to receive the results
          as a list of tuple or a pandas DataFrame. Defaults to True.

    Returns:
        Either a pandas DataFrame or a list of tuples, depending on the
        as_pandas boolean.
    """
    if not as_pandas:
      return [(name, helper.help) for name, helper in cls._helpers.items()]

    lines = []
    for name, helper in cls._helpers.items():
      hints = helper.types
      hint_strings = []
      for key, value in hints.items():
        value_string = getattr(value, '__name__', str(value))
        hint_strings.append(f'{key} [{value_string}]')
      helper_string = ', '.join(hint_strings)

      lines.append({
          'name': name,
          'help': helper.help,
          'arguments': helper_string,
      })
    return pandas.DataFrame(lines)

  @classmethod
  def get_magic_info(cls, as_pandas: Optional[bool] = True) -> Union[
      pandas.DataFrame, List[Tuple[Text, Text]]]:
    """Get a list of all magics.

    Args:
      as_pandas (bool): boolean to determine whether to receive the results
          as a list of tuples or a pandas DataFrame. Defaults to True.

    Returns:
      Either a pandas DataFrame or a list of tuples, depending on the as_pandas
      boolean.
    """
    if not as_pandas:
      return [(x.magic_name, x.__doc__.split('\n')[0]) for x in iter(
          cls._magics.values())]

    entries = []
    for magic_name, magic_class in iter(cls._magics.items()):
      description = magic_class.__doc__.split('\n')[0]
      magic_dict = {
          'name': magic_name,
          'cell': f'%%{magic_name}',
          'line': f'%{magic_name}',
          'function': f'{magic_name}_func',
          'description': description}
      entries.append(magic_dict)

    df = pandas.DataFrame(entries)
    return df[cls.MAGICS_DF_COLUMNS].sort_values('name')

  @classmethod
  def register_helper(
      cls, name: Text, helper: Any, typing_help: Dict[Text, Any]):
    """Register a picatrix helper function.

    Args:
      name (str): the name of the helper function.
      helper (function): the helper function to register.
      typing_help (dict): dict with the arguments and their types.

    Raises:
      KeyError: if the helper is already registered.
    """
    if name in cls._helpers:
      raise KeyError(
          f'The helper [{name}] is already registered.')
    doc_string = helper.__doc__
    if doc_string:
      help_string = doc_string.split('\n')[0]
    else:
      help_string = 'No help string supplied.'

    cls._helpers[name] = Helper(
        function=helper, help=help_string, types=typing_help)

  @classmethod
  def register_magic(
      cls, function: Callable[[Text, Text], Text],
      conditional: Callable[[], bool] = None):
    """Register magic function as a magic in picatrix.

    Args:
      function (function): the function to register as a line and a
          cell magic.
      conditional (function): a function that should return a bool, used to
          determine whether to register magic or not. This can be used by
          magics to determine whether a magic should be registered or not, for
          instance basing that on whether the notebook is able to reach the
          required service, or whether a connection to a client can be achieved,
          etc. This is optional and if not provided a magic will be registered.

    Raises:
      KeyError: if the magic is already registered.
    """
    if conditional and not conditional():
      return

    magic_name = function.magic_name

    if magic_name in cls._magics:
      raise KeyError(
          f'The magic [{magic_name}] is already registered.')

    ip = get_ipython()
    if ip:
      ip.register_magic_function(
          function, magic_kind='line_cell', magic_name=magic_name)

    cls._magics[magic_name] = function
    function_name = f'{magic_name}_func'

    def capture_output(function, name):
      """A function that wraps around magic functions to capture output."""
      @functools.wraps(function)
      def wrapper(*args, **kwargs):
        function_output = function(*args, **kwargs)
        state_obj = state.state()
        return state_obj.set_output(function_output, magic_name=name)
      return wrapper

    _ = utils.ipython_bind_global(
        function_name, capture_output(function.fn, function_name))
