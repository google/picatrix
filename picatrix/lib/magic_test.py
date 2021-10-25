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
# pylint: disable=unused-argument
"""Test for Picatrix integration with IPython magics."""

from typing import Text

import pytest

from .magic import (
    MagicArgParsingError,
    MagicArgs,
    MagicParsingError,
    MagicType,
    _MagicSpec,
)


# Test functions
def magic(
    a: Text,
    b: Text,
):
  """Example function.

    Args:
      a: first argument
      b: second argument
    """


def test_magicspec_valid():
  """Test if _MagicSpec parses simple function."""

  want = _MagicSpec(
      name="magic",
      docstring=magic.__doc__,
      typ=MagicType.LINE,
      args_with_no_defaults=["a", "b"],
      args_descriptions={
          "a": "first argument",
          "b": "second argument",
      },
      args_types={
          "a": str,
          "b": str,
      })
  got = _MagicSpec.from_function(MagicType.LINE, magic)

  assert want == got


def magic_with_defaults(
    a: Text,
    b: Text = "dog",
    c: Text = "cat",
):
  """Example function.

    Args:
      a: first argument
      b: second argument
      c: third argument
    """


def test_magicspec_valid_with_defaults():
  """Test if _MagicSpec parses simple function with default value."""

  want = _MagicSpec(
      name="magic_with_defaults",
      docstring=magic_with_defaults.__doc__,
      typ=MagicType.LINE,
      args_with_no_defaults=["a"],
      args_with_defaults={
          "b": "dog",
          "c": "cat",
      },
      args_descriptions={
          "a": "first argument",
          "b": "second argument",
          "c": "third argument",
      },
      args_types={
          "a": str,
          "b": str,
          "c": str,
      })
  got = _MagicSpec.from_function(MagicType.LINE, magic_with_defaults)

  assert want == got


# pylint: disable=missing-function-docstring
def magic_no_docstring(
    a: Text,
    b: Text = "dog",
):
  pass


# pylint: enable=missing-function-docstring


def test_magicspec_no_docstring():
  """Test if _MagicSpec errors on function with no docstring."""

  with pytest.raises(MagicParsingError):
    _MagicSpec.from_function(MagicType.LINE, magic_no_docstring)


def magic_bad_docstring(
    a: Text,
    b: Text = "dog",
):
  """Example function.

    Args:
      a: first argument
    """


def test_magicspec_bad_docstring():
  """Test if _MagicSpec errors on function with no docstring for all args."""

  with pytest.raises(MagicParsingError):
    _MagicSpec.from_function(MagicType.LINE, magic_bad_docstring)


def magic_notstring(
    a: int,
    b: Text = "dog",
    c: float = 1.11,
):
  """Example function.

    Args:
      a: first argument
      b: second argument
      c: third argument
    """


def test_magicspec_nonstring():
  """Test if _MagicSpec errors on non-string parameter."""

  want = _MagicSpec(
      name="magic_notstring",
      docstring=magic_notstring.__doc__,
      typ=MagicType.LINE,
      args_with_no_defaults=["a"],
      args_with_defaults={
          "b": "dog",
          "c": 1.11,
      },
      args_descriptions={
          "a": "first argument",
          "b": "second argument",
          "c": "third argument",
      },
      args_types={
          "a": int,
          "b": str,
          "c": float,
      })
  got = _MagicSpec.from_function(MagicType.LINE, magic_notstring)

  assert want == got


def magic_variadic(
    a: Text,
    *args: Text,
) -> Text:
  """Example function.

    Args:
      a: first argument
      *args: all other arguments
  """


def test_magicspec_variadic():
  """Test if _MagicSpec errors on functions with variadic params."""

  with pytest.raises(MagicParsingError):
    _MagicSpec.from_function(MagicType.LINE, magic_variadic)


def magic_kwvariadic(
    a: Text,
    **kwargs: Text,
) -> Text:
  """Example function.

    Args:
      a: first argument
      **kwargs: all other arguments
    """


def test_magicspec_kwvariadic():
  """Test if _MagicSpec errors on functions with keyword variadic params."""

  with pytest.raises(MagicParsingError):
    _MagicSpec.from_function(MagicType.LINE, magic_kwvariadic)


def magic_with_all_defaults(
    a: Text = "dog",
    b: Text = "cat",
):
  """Example function.

    Args:
      a: first argument
      b: second argument
  """


def test_magicsargsparser_empty():
  """Test parsing of empty string."""

  spec = _MagicSpec.from_function(MagicType.LINE, magic_with_all_defaults)
  parser = spec.to_parser()

  line = ""
  want = MagicArgs(
      bind_variable="_", kwargs={
          "a": "dog",
          "b": "cat",
      })
  got = parser.parse_magic_args(line, None)
  assert want == got


def test_magicsargsparser_positional():
  """Test parsing of a signal positional argument."""
  spec = _MagicSpec.from_function(MagicType.LINE, magic_with_defaults)
  parser = spec.to_parser()

  line = "v -- horse"
  want = MagicArgs(
      bind_variable="v", kwargs={
          "a": "horse",
          "b": "dog",
          "c": "cat",
      })
  got = parser.parse_magic_args(line, None)
  assert want == got


def test_magicsargsparser_mixed():
  """Test parsing of a mix of positional and keyword arguments."""
  spec = _MagicSpec.from_function(MagicType.LINE, magic_with_defaults)
  parser = spec.to_parser()

  line = "-- --b=boar horse"
  want = MagicArgs(
      bind_variable="_", kwargs={
          "a": "horse",
          "b": "boar",
          "c": "cat",
      })
  got = parser.parse_magic_args(line, None)
  assert want == got


def test_magicsargsparser_notstring():
  """Test parsing of non-string arguments."""
  spec = _MagicSpec.from_function(MagicType.LINE, magic_notstring)
  parser = spec.to_parser()

  line = "-- --b=boar --c=2.22 10"
  want = MagicArgs(
      bind_variable="_", kwargs={
          "a": 10,
          "b": "boar",
          "c": 2.22,
      })
  got = parser.parse_magic_args(line, None)
  assert want == got


def magic_bool_true(a: bool = True):
  """Example function.

    Args:
      a: first argument
  """


def test_magicsargsparser_bool_true():
  """Test parsing of boolean argument with default equal to true."""
  spec = _MagicSpec.from_function(MagicType.LINE, magic_bool_true)
  parser = spec.to_parser()

  line = "-- --a"
  want = MagicArgs(bind_variable="_", kwargs={"a": False})
  got = parser.parse_magic_args(line, None)
  assert want == got

  line = ""
  want = MagicArgs(bind_variable="_", kwargs={"a": True})
  got = parser.parse_magic_args(line, None)
  assert want == got


def magic_bool_false(a: bool = False):
  """Example function.

    Args:
      a: first argument
  """


def test_magicsargsparser_bool_false():
  """Test parsing of boolean argument with default equal to false."""
  spec = _MagicSpec.from_function(MagicType.LINE, magic_bool_false)
  parser = spec.to_parser()

  line = "-- --a"
  want = MagicArgs(bind_variable="_", kwargs={"a": True})
  got = parser.parse_magic_args(line, None)
  assert want == got

  line = ""
  want = MagicArgs(bind_variable="_", kwargs={"a": False})
  got = parser.parse_magic_args(line, None)
  assert want == got


@pytest.mark.parametrize("line", ["--", " -- ", "-- --b=cat", "11 -- cat"])
def test_magicsargsparser_error(line):
  """Test parsing behavior for errornous inputs."""
  spec = _MagicSpec.from_function(MagicType.LINE, magic_with_defaults)
  parser = spec.to_parser()

  with pytest.raises(MagicArgParsingError):
    _ = parser.parse_magic_args(line, None)
