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
from typing import Tuple, Union, Optional

import pandas
import ipyaggrid

try:
  # 3rd party widgets do not work inside colab, we will use the
  # built-in data table instead there.
  from google.colab.data_table import DataTable
except ImportError:
  DataTable = None

from picatrix.lib import framework


DEFAULT_COLUMNS_HIDE = ('_type', '_id', '__ts_emojis', '_index')


@framework.picatrix_helper
def display_table(
    data_frame: pandas.DataFrame,
    hide_columns: Optional[Tuple[str]] = None) -> Union[
        ipyaggrid.grid.Grid, DataTable]:
  """Display a dataframe interactively with a toolbar."""
  if DataTable:
    return DataTable(data_frame, include_index=False)

  column_defs = []

  if hide_columns is None:
    hide_columns = DEFAULT_COLUMNS_HIDE

  for column in data_frame.columns:
    pivot_group = column != 'message'
    hide = False
    if column in hide_columns:
      hide = True
      pivot_group = False

    column_dict = {
        'headerName': column.title(),
        'field': column,
        'rowGroup': False,
        'enableRowGroup': True,
        'hide': hide,
        'pivot': pivot_group,
        'sortable': True,
        'resizable': True,
    }

    column_defs.append(column_dict)

  grid_options = {
      'columnDefs' : column_defs,
      'enableSorting': True,
      'enableFilter': True,
      'enableColResize': True,
      'enableRangeSelection': True,
      'editable': False,
      'rowGroupPanelShow': 'always',
      'rowSelection': 'multiple',
  }

  return ipyaggrid.Grid(
      grid_data=data_frame,
      quick_filter=True,
      show_toggle_edit=False,
      export_csv=True,
      export_excel=False,
      export_to_df=False,
      theme='ag-theme-balham',
      show_toggle_delete=False,
      columns_fit='auto',
      index=False,
      grid_options=grid_options,
      keep_multiindex=True,
  )
