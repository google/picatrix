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
"""Class that defines common picatrix magics."""

from typing import Any
from typing import Optional
from typing import Text

import pandas

from picatrix.lib import framework
from picatrix.lib import manager
from picatrix.lib import state


@framework.picatrix_magic
def picatrixhelpers(data: Optional[Text] = '') -> pandas.DataFrame:
  """Provides information about registered Picatrix helpers.

  Args:
    data (str): If empty an overview of all registered helpers is provided,
        otherwise the help message of a particular helper is provided.

  Returns:
      A pandas DataFrame that contains the names and basic information about
      every registered helper or information about a single helper if
      the data string is provided.
  """
  info_df = manager.MagicManager.get_helper_info(as_pandas=True)
  if not data:
    return info_df

  helper_obj = manager.MagicManager.get_helper(data)
  if not helper_obj:
    return pandas.DataFrame()

  return info_df[info_df.name == data.strip()]


@framework.picatrix_magic
def picatrixmagics(data: Optional[Text] = '') -> pandas.DataFrame:
  """Provides information about registered Picatrix magics.

  Args:
    data (str): If empty an overview of all registered magics is provided,
        otherwise the help message of a particular magic is provided.

  Returns:
      A pandas DataFrame that contains the names and basic information about
      every registered magic or information about a single magic if
      the data string is provided.
  """
  if not data:
    return manager.MagicManager.get_magic_info(as_pandas=True)

  magic_obj = manager.MagicManager.get_magic(data)

  if not magic_obj:
    return pandas.DataFrame()

  description = magic_obj.__doc__.split('\n')[0]
  return pandas.DataFrame([{
      'name': magic_obj.magic_name,
      'description': description,
      'function': '{0:s}_func'.format(magic_obj.magic_name),
      'help': magic_obj.argument_parser.format_help()}])


# pylint: disable=unused-argument
@framework.picatrix_magic
def last_output(data: Optional[Text] = '') -> Any:
  """Returns the last output from a magic that was executed.

  Args:
    data (str): optional string that does nothing.

  Returns:
    The last output from a magic that was run.
  """
  state_obj = state.state()
  output = state_obj.last_output

  return output
