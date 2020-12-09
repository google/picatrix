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
"""Defines helper functions to display tables or dataframes."""

import qgrid

from picatrix.lib import framework


@framework.picatrix_helper
def display_table(data_frame, show_toolbar=False, visible_rows=20):
  """Display a dataframe interactively with a toolbar to select."""
  grid_options = {
      'enableColumnReorder': True,
      'enableTextSelectionOnCells': True,
      'editable': False,
      'maxVisibleRows': visible_rows,
      'highlightSelectedRow': True,
  }

  column_options = {
      'editable': False,
  }

  return qgrid.show_grid(
      data_frame,
      precision=5,
      column_options=column_options,
      show_toolbar=show_toolbar,
      grid_options=grid_options)
