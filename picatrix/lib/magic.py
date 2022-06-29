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
"""Types and functions defining Picatrix integration with IPython magics."""

import argparse
import shlex
from dataclasses import dataclass, field
from enum import Enum, auto
from inspect import getfullargspec
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NoReturn,
    Optional,
    Text,
    Type,
    Union,
)

from docstring_parser import parse

from .error import Error
from .utils import ipython_bind_global


class MagicError(Error):
  """Generic Picatrix error related to IPython magics."""


class MagicParsingError(MagicError, ValueError):
  """Raised when invalid function is provided to magic framework."""


class MagicArgParsingError(MagicError, ValueError):
  """Raised when invalid arguments where provided to magic."""


class MagicType(Enum):
  """Enum indicating a type of the IPython magic."""
  CELL = auto()
  LINE = auto()


_MagicArgValues = [bool, int, float, str]
MagicArgValue = Union[bool, int, float, str]
_MagicArgValueType = Union[Type[bool], Type[int], Type[float], Type[str]]


def _validate_arg_value(arg: Text, v: Any) -> MagicArgValue:
  for typ in _MagicArgValues:
    if isinstance(v, typ):
      return typ(v)
  raise MagicArgParsingError(
      f"{arg}=\"{v}\" is of invalid type; has to be {MagicArgValue}")


@dataclass(frozen=True)
class MagicArgs:
  """Arguments parsed out of IPython magic invocation."""
  bind_variable: Text = field(default="_")
  kwargs: Dict[Text, MagicArgValue] = field(default_factory=dict)

  def __post_init__(self):
    if not self.bind_variable.isidentifier():  # pylint: disable=no-member
      raise MagicArgParsingError(
          f"\"{self.bind_variable}\" isn't valid Python "
          "identifier, see: "
          "https://docs.python.org/3/reference/"
          "lexical_analysis.html#identifiers")


class ArgParserNonZeroStatus(Exception):
  """Raised when the argument parser has exited with non-zero status."""


class MagicArgumentParser(argparse.ArgumentParser):
  """Argument parser for Picatrix magics."""

  def exit(self, status: int = 0, message: Optional[Text] = None) -> NoReturn:
    """Exiting method for argument parser.

    Args:
      status (int): exit status of the parser.
      message (str): the error message.

    Raises:
      MagicArgParsingError: when the parser is unable to parse the arguments.
      ArgParserNonZeroStatus: when the parser has successfully completed.
    """
    if not status:
      raise ArgParserNonZeroStatus()

    if message:
      raise MagicArgParsingError(message.strip())

    raise MagicArgParsingError("Wrong usage.")

  def parse_magic_args(
      self, line: Text, cell: Optional[Text] = None) -> MagicArgs:
    """Parse arguments out of line and cell content as provided by IPython."""
    line = line.strip()

    kwargs: Dict[Text, MagicArgValue] = {}
    if cell:
      kwargs["cell"] = cell

    if line and "-- " not in line:
      return MagicArgs(bind_variable=line, kwargs=kwargs)
    if line.endswith("--"):
      return MagicArgs(bind_variable=line.rstrip("--"), kwargs=kwargs)

    if not line:
      bind_variable = "_"
      raw = line
    elif line.startswith("-- "):
      bind_variable = "_"
      raw = line[3:]
    else:
      bind_variable, raw = line.split(" -- ", maxsplit=1)

    for arg, value in self.parse_args(shlex.split(raw)).__dict__.items():
      kwargs[str(arg)] = _validate_arg_value(arg, value)

    return MagicArgs(bind_variable, kwargs)


def _usage_string(
    mtyp: MagicType, args: Iterable[Text], kwargs: Iterable[Text]) -> Text:
  arguments = (
      " ".join(f"[--{key} {key.upper()}]" for key in kwargs) + " " +
      " ".join(args))

  if mtyp == MagicType.LINE:
    return f"\n```%%%(prog)s [bind_variable] -- [-h] {arguments}```"
  else:
    return f"\n```\n%%%%%(prog)s [bind_variable] -- [-h] {arguments}\ncell\n```"


@dataclass(frozen=True)
class _MagicSpec:
  """Magic function specification for argument parsing purposes."""
  name: Text
  docstring: Text
  typ: MagicType

  args_with_no_defaults: List[Text] = field(default_factory=list)
  args_with_defaults: Dict[Text, Text] = field(default_factory=dict)
  args_descriptions: Dict[Text, Text] = field(default_factory=dict)
  args_types: Dict[Text, _MagicArgValueType] = field(default_factory=dict)

  def __post_init__(self):
    if (self.args_with_no_defaults or
        self.args_with_defaults) and not self.args_descriptions:
      raise MagicParsingError(
          "Magics have to have docstring section describing their arguments.")
    # pylint: disable=unsupported-membership-test
    for arg, typ in self.args_types.items():
      if typ == bool and arg in self.args_with_no_defaults:
        raise MagicParsingError(
            "Arguments of type bool have to have a default value specified.")
    for arg in list(self.args_with_no_defaults) + list(self.args_with_defaults):
      if arg not in self.args_descriptions:
        raise MagicParsingError(
            "Magics have to have docstring section describing all of their "
            f"arguments; docstring missing for `{arg}`")
    if self.typ == MagicType.CELL and "cell" not in self.args_with_no_defaults:
      raise MagicParsingError(
          "Cell magics have to have positional argument called `cell`")
    # pylint: enable=unsupported-membership-test

  @classmethod
  def from_function(
      cls,
      typ: MagicType,
      func: Callable[..., Any],
      name: Optional[Text] = None) -> "_MagicSpec":
    """Creates _MagicSpec from compatible function."""
    name = name if name else func.__name__

    if not name.isidentifier():
      raise MagicParsingError(
          f"\"{name}\" isn't valid Python identifier, see: "
          "https://docs.python.org/3/reference/"
          "lexical_analysis.html#identifiers")
    if not func.__doc__:
      raise MagicParsingError("Magics have to have docstring.")

    spec = getfullargspec(func)
    if spec.varargs or spec.varkw:
      raise MagicParsingError(
          "Magics can't have explicit variadic arguments, "
          "i.e. `*args` or `**kwargs`")
    if spec.kwonlyargs and not spec.kwonlydefaults:
      raise MagicParsingError(
          "Magics can't have keyword-only arguments without default value.")

    args: List[Text] = spec.args
    args_with_defaults: Dict[Text, Text] = {}
    args_types: Dict[Text, _MagicArgValueType] = {}

    if spec.annotations:
      for arg, typ_ in spec.annotations.items():
        if arg == "return" or typ_ in _MagicArgValues:
          args_types[arg] = typ_
        else:
          raise MagicParsingError(
              f"Magics can only have arguments of type {MagicArgValue}; "
              f"got {arg}: {typ_}")

    if spec.defaults:
      for default in reversed(spec.defaults):
        args_with_defaults[args.pop()] = default

    if spec.kwonlydefaults:
      for arg, default in spec.kwonlydefaults.items():
        args_with_defaults[arg] = default

    docstring = func.__doc__ if func.__doc__ else ""

    args_descriptions: Dict[Text, Text] = {
        param.arg_name: param.description  # type: ignore
        for param in parse(docstring).params
    }

    return cls(
        name, docstring, typ, args, args_with_defaults, args_descriptions,
        args_types)

  def to_parser(self) -> MagicArgumentParser:
    """Create an argument parser out of _MagicSpec."""
    desc, *_ = self.docstring.split('\n')

    visible_args = self.args_with_no_defaults
    if self.typ == MagicType.CELL:
      visible_args = [a for a in self.args_with_no_defaults if a != "cell"]
    parser = MagicArgumentParser(
        prog=self.name,
        description=desc,
        usage=_usage_string(
            self.typ, visible_args, self.args_with_defaults.keys()))  # pylint: disable=no-member

    for arg in self.args_with_no_defaults:  # pylint: disable=not-an-iterable
      if self.typ == MagicType.CELL and arg == "cell":
        continue
      typ = self.args_types.get(arg, str)
      parser.add_argument(
          arg,
          type=typ,  # type: ignore
          action="store",
          help=self.args_descriptions[arg])
    for arg, default in self.args_with_defaults.items():  # pylint: disable=no-member
      typ = self.args_types.get(arg, str)
      if typ == bool:
        parser.add_argument(
            f"--{arg}",
            dest=arg,
            action="store_false" if default else "store_true",
            help=self.args_descriptions[arg],
            default=default)
      else:
        parser.add_argument(
            f"--{arg}",
            dest=arg,
            type=typ,  # type: ignore
            action="store",
            help=self.args_descriptions[arg],
            default=default)
    return parser


@dataclass(frozen=True)
class Magic:
  """Wrapper for IPython magic."""
  _spec: _MagicSpec
  _parser: MagicArgumentParser
  func: Callable[..., Any]
  __doc__: Text

  @classmethod
  def wrap(
      cls,
      typ: MagicType,
      func: Callable[..., Any],
      name: Optional[Text] = None) -> "Magic":
    """Wrap wraps a function to make it an IPython magic."""
    spec = _MagicSpec.from_function(typ, func, name=name)
    return cls(spec, spec.to_parser(), func, func.__doc__ or cls.__doc__)

  def __call__(self, line: Text, cell: Optional[Text] = None) -> Any:
    try:
      args = self._parser.parse_magic_args(line, cell)
      res = self.func(**args.kwargs)
      ipython_bind_global(args.bind_variable, res)
      return res
    except ArgParserNonZeroStatus:
      return None
