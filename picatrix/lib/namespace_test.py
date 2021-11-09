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
# pylint: disable=W0212
"""Test for Picatrix namespacing."""

from typing import Union

import pandas as pd
import pytest

from .namespace import Namespace, NamespaceKeyError


def test_invalid_key():
  """Test if namespace throws an error on invalid key names."""
  n = Namespace[int](name="n", docstring="Example namespace")
  with pytest.raises(NamespaceKeyError):
    n._add("1aa", 1)


def test_similar_key():
  """Test if namespace throws an  helpful error on typos."""
  n = Namespace[int](name="n", docstring="Example namespace")
  n._add("apple", 1)
  n._add("orange", 2)
  n._add("carrot", 3)

  with pytest.raises(NamespaceKeyError) as exc:
    _ = n.aple

  assert "did you mean \"apple\"" in str(exc)


def test_to_frame():
  """Test namespaces .to_frame functionality for nested namespaces."""
  n = Namespace[Union[int, Namespace[int]]](
      name="n", docstring="Example namespace")
  n._add("apple", 1)
  n._add("orange", 2)
  n._add("carrot", 3)
  n._add("nn", Namespace[int](name="n.nn", docstring="Nested namespace"))
  n.nn._add("dog", 11)
  n._add("tomato", 4)

  a = 1
  inttyp = str(type(a))
  intdoc = a.__doc__
  intdesc, *_ = intdoc.split("\n")

  want = pd.DataFrame.from_records(
      [
          {
              "Name": "n",
              "Type": "Namespace",
              "Description": "Example namespace",
              "Docstring": "Example namespace",
          },
          {
              "Name": "n.apple",
              "Type": inttyp,
              "Description": intdesc,
              "Docstring": intdoc,
          },
          {
              "Name": "n.orange",
              "Type": inttyp,
              "Description": intdesc,
              "Docstring": intdoc,
          },
          {
              "Name": "n.carrot",
              "Type": inttyp,
              "Description": intdesc,
              "Docstring": intdoc,
          },
          {
              "Name": "n.nn",
              "Type": "Namespace",
              "Description": "Nested namespace",
              "Docstring": "Nested namespace",
          },
          {
              "Name": "n.nn.dog",
              "Type": inttyp,
              "Description": intdesc,
              "Docstring": intdoc,
          },
          {
              "Name": "n.tomato",
              "Type": inttyp,
              "Description": intdesc,
              "Docstring": intdoc,
          },
      ])
  got = n.to_frame(with_doc=True)
  assert want.equals(got)
