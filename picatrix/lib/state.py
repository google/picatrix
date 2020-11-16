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
"""Class that defines the state, which ."""
import logging
import threading

from typing import Any
from typing import Dict
from typing import Optional
from typing import Text

from picatrix.lib import utils


logger = logging.getLogger('picatrix.state')

__state = None
_LOCK = threading.Lock()


def state(refresh_state: bool = False):
  """Property that returns a state object."""
  # pylint: disable=global-statement
  # Making sure we have only one state object.
  global __state

  with _LOCK:
    if refresh_state or __state is None:
      __state = State()

    return __state


class State:
  """Picatrix state object."""

  _cache: Dict[Text, Any] = {}
  _last_output: Any
  _last_magic: Text

  def __init__(self):
    self._last_output = None
    self._last_magic = ''

  @property
  def last_magic(self):
    """A property that returns the last magic that was run."""
    return self._last_magic

  @property
  def last_output(self):
    """A property that returns the last output from a magic."""
    return self._last_output

  def add_to_cache(self, name: Text, value: Any):
    """Add a value to the cache or update value if it exists.

    Args:
      name (str): name of the value in the cache.
      value (object): the value to be stored in the cache.
    """
    with _LOCK:
      self._cache[name] = value

  def get_from_cache(self, name: Text, default: Optional[Any] = None) -> Any:
    """Get a value from the cache.

    Args:
      name (str): name of the value in the cache to retrieve.
      default (object): if the value does not exist, defines the default
          value to return. This is optional and returns None if not defined.

    Returns:
      The value from the cache if it exists, otherwise the default value.
    """
    with _LOCK:
      return self._cache.get(name, default)

  def remove_from_cache(self, name: Text):
    """Removes a value from the cache if it exists."""
    with _LOCK:
      if name in self._cache:
        del self._cache[name]

  def set_output(
      self, output: Any, magic_name: Text,
      bind_to: Optional[Text] = '') -> Optional[Any]:
    """Sets an output from a magic and stores it in the namespace if needed.

    Args:
      output (object): the output from the magic as executed.
      magic_name (str): the name of the magic that was used.
      bind_to (str): optional name of a variable. If this is provided
        the output is omitted and variable is stored in the namespace using
        the name provided here.

    Returns:
      Returns the output object.
    """
    with _LOCK:
      self._last_output = output
      self._last_magic = magic_name

      if bind_to:
        _ = utils.ipython_bind_global(name=bind_to, value=output)
        return None

      return output
