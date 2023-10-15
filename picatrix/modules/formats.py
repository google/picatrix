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
"""Functions and magics for handling popular data formats."""

import json as _json
from io import StringIO
from typing import Any, Dict, Text

import pandas

from picatrix import new_cell_magic


@new_cell_magic
def text(cell: Text) -> Text:
  """Ingest the cell content as raw text without evaluating escape codes.
  
  Args:
    cell: text to be loaded

  Returns:
    cell text
  """
  return cell


@new_cell_magic
def csv(
    cell: Text,
    sep: Text = ",",
    quotechar: Text = "\"",
    doublequote: bool = True,
    escapechar: Text = "\\",
) -> pandas.DataFrame:
  """Parse cell content as a CSV data and create a pandas DataFrame.
  
  The function uses pandas.read_csv function to parse the text:
  https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

  Args:
    cell: text to be parsed as CSV
    sep: Delimiter to use
    quotechar: The character used to denote the start and end of a 
      quoted item. Quoted items can include the delimiter and it 
      will be ignored.
    doublequote: a flag determining whether or not to interpret two 
      consecutive quotechar elements INSIDE a field as a single 
      quotechar element.
    escapechar: One-character string used to escape other characters.

  Returns:
    pandas DataFrame constructed from the CSV.
  """
  return pandas.read_csv( # type: ignore
      StringIO(cell),
      sep=sep,
      quotechar=quotechar,
      doublequote=doublequote,
      escapechar=escapechar,
  )


@new_cell_magic
def json(cell: Text) -> Dict[Text, Any]:
  """Parse cell content as a JSON object and create a Python dict.

  The function uses json.load function to parse the text:
  https://docs.python.org/3/library/json.html#json.load
  
  Args:
    cell: text to be parsed as JSON
    
  Returns:
    a Python dict construced from the JSON
  """
  return _json.loads(cell)
