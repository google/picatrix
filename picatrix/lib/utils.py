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
"""Common reusable components for picatrix."""
import sys

from typing import Any
from typing import Optional
from typing import Text

from IPython import get_ipython
from IPython.display import clear_output


def ask_question(question: Text, input_type: Optional[Any] = Text) -> Any:
  """Asks a question and returns the answer.

  Args:
    question (str): the question to be asked.
    input_type (object): the type of the input data.

  Raises:
    TypeError: if the input type is not supported.

  Returns:
    object: an object of type "input_type" read back as an answer.
  """
  print(question)
  answer_line = sys.stdin.readline()
  answer_line = answer_line.strip()

  if input_type == str:
    return answer_line

  if input_type in (int, float):
    return input_type(answer_line)

  raise TypeError('Only support str, int and float as input types')


def clear_notebook_output():
  """Clears the output cell from the notebook."""
  clear_output(wait=True)


def ipython_bind_global(name: Text, value: Any) -> Any:
  """Binds the name to a Python object denoted by value.

  Args:
    name (str): Variable name.
    value (object): Python object to bind to name

  Returns:
    Returns the value bound to the given name.
  """
  ip = get_ipython()
  if ip and name:
    ip.push({name: value})
  return value


def ipython_get_global(name: Text) -> Any:
  """Returns the Python object bound to the given name in the user namespace.

  Args:
    name (str): Variable name.

  Returns:
    Returns the value bound to the given name.

  Raises:
    KeyError: if the variable is not stored in the namespace.
  """
  ip = get_ipython()
  return ip.all_ns_refs[0][name]


def ipython_remove_global(name: Text):
  """Removes a Python object that is bound to the user namespace.

  Args:
    name (str): Variable name.

  Raises:
    KeyError: if the variable is not stored in the namespace.
  """
  ip = get_ipython()
  namespace = ip.all_ns_refs[0]

  if name not in namespace:
    raise KeyError(f'The variable {name} is not currently in the namespace.')

  _ = namespace.pop(name)
