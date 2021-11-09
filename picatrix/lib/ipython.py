# Copyright 2021 Google LLC
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

# type: ignore
"""Helper function for Picatrix IPython magic handling.

This module exists mostly because of IPython non-strict type checking which
annoys pyright. Type checking is disabled for this module so tread lightly.
"""

from typing import Any, Callable, Text, Union

from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell


def add_line_magic(name: Text, magic: Callable[..., Any]):
  """Adds new IPython line magic (`%magic`)."""
  ip: Union[InteractiveShell, None] = get_ipython()
  if not ip:
    return
  ip.register_magic_function(magic, magic_kind="line", magic_name=name)


def add_cell_magic(name: Text, magic: Callable[..., Any]):
  """Adds new IPython line magic (`%%magic`)."""
  ip: Union[InteractiveShell, None] = get_ipython()
  if not ip:
    return
  ip.register_magic_function(magic, magic_kind="cell", magic_name=name)


def delete_magic(name: Text):
  """Deletes IPython magic based on name."""
  ip: Union[InteractiveShell, None] = get_ipython()
  if not ip:
    return

  line_magics = ip.magics_manager.magics.get("line", {})
  if name in line_magics:
    _ = ip.magics_manager.magics["line"].pop(name)
  cell_magics = ip.magics_manager.magics.get("cell", {})
  if name in cell_magics:
    _ = ip.magics_manager.magics["cell"].pop(name)
