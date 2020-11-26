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
"""Class that defines the framework for exported magics and functions."""

import argparse
import functools
import inspect
import types
import typing

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Text
try:
  # Got introduced in python 3.8.
  from typing import Protocol
except ImportError:
  from typing_extensions import Protocol

from picatrix.lib import error
from picatrix.lib import manager
from picatrix.lib import state
from picatrix.lib import utils


class MagicProtocol(Protocol):
  """Simple Typing protocol class for magic functions."""

  def __call__(self, *args: Any) -> Any:
    pass


class MagicArgument:
  """Simple Argument holder for magic arguments."""

  def __init__(self, *argc, **kwargs):
    self.argc = argc
    self.kwargs = kwargs


class MagicArgumentParser(argparse.ArgumentParser):
  """Argument parser for picatrix magics."""

  def __init__(self, *args, **kwargs):
    super(MagicArgumentParser, self).__init__(*args, **kwargs)
    self.storage = {}

  def exit(self, status: Optional[int] = 0, message: Optional[Text] = ''):
    """Exiting method for argument parser.

    Args:
      status (int): exit status of the parser.
      message (str): the error message.

    Raises:
      KeyError: when the parser is unable to parse the arguments.
      error.ArgParserNonZeroStatus: when the parser has successfully completed.
    """
    if not status:
      raise error.ArgParserNonZeroStatus('Exiting.')

    if message:
      raise KeyError('Wrong usage: {0:s}'.format(message.strip()))

    raise KeyError('Wrong usage, no further error message supplied.')


class _Magic:
  """The Picatrix Magic decorator."""

  argument_parser: MagicArgumentParser
  magic_name: Text

  def __init__(
      self, fn: MagicProtocol, arguments: Optional[List[MagicArgument]] = None,
      name_func: Optional[Callable[[Text], Text]] = None):
    """Initialize the Picatrix Magic."""
    self.fn = fn
    if name_func:
      self.magic_name = name_func(fn.__name__)
    else:
      self.magic_name = fn.__name__

    functools.update_wrapper(self, fn)
    self.__name__ = self.magic_name

    # pylint: disable=access-member-before-definition
    first_line = self.__doc__.split('\n')[0]
    self.argument_parser = MagicArgumentParser(
        prog=self.magic_name,
        description=first_line,
        usage=(
            '%%%(prog)s [arguments] data\nor\n%%%%%(prog)s [arguments]\ndata'))

    if arguments:
      for argument in arguments:
        dest_name = argument.kwargs.get('dest')
        type_string = argument.kwargs.get('type')
        # We need to check whether the custom argument contains an object
        # type, if so we will need to change it into a str and store the
        # type in the argument parser so it can be confirmed after variable
        # expansion.
        if dest_name and type_string:
          if isinstance(type_string, type):
            type_string = str(type_string).split('\'')[1]
          if type_string not in ('str', 'int', 'bool', 'float', 'unicode'):
            self.argument_parser.storage[dest_name] = type_string
            argument.kwargs['type'] = str

        self.argument_parser.add_argument(*argument.argc, **argument.kwargs)
    else:
      _add_function_arguments_to_parser(fn, self.argument_parser)

    try:
      self.argument_parser.add_argument(
          '--bindto', '-bindto',
          type=str,
          default='',
          action='store',
          dest='bindto',
          help='Bind the results to a variable instead of being returned.')
    except argparse.ArgumentError:
      pass

    try:
      self.argument_parser.add_argument(
          'data', nargs='?',
          help=self.argument_parser.storage.get('_data_help', ''))
    except argparse.ArgumentError:
      pass

    self.__doc__ = self.argument_parser.format_help()

  # pylint: disable=inconsistent-return-statements
  def __call__(self, line: Text, cell: Optional[Text] = None) -> Optional[Any]:
    line_magic = cell is None

    arguments = _parse_line_string(line)

    try:
      options = self.argument_parser.parse_args(arguments)
    except KeyError as e:
      print((
          'Unable to parse arguments, with error: {0!s}.\n'
          'Correct usage is: {1:s}').format(
              e, self.argument_parser.format_help()))
      return
    except error.ArgParserNonZeroStatus:
      # When argparser ends execution but without an error this exception
      # is raised, eg: when "-h" or help is used. In those cases we need
      # to return without running the magic function.
      return

    if not line_magic:
      variable = options.data
      options.data = cell

    bind_to = options.bindto
    option_dict = options.__dict__
    del option_dict['bindto']

    # TODO: Change this so that there is no variable expansion
    # done by the core and all variable expansion is only done here.
    for key, value in iter(option_dict.items()):
      if not value:
        continue

      if not isinstance(value, str):
        continue

      if value[0] == '{' and value[-1] == '}':
        var_name = value[1:-1]
        var_type = self.argument_parser.storage.get(key)

        if '{' not in var_name and '}' not in var_name:
          var_obj = utils.ipython_get_global(var_name)
          if var_type and var_type != 'object':
            type_string = type(var_obj).__name__
            if (type_string != var_type) and not type_string.endswith(
                var_type) and not var_type.endswith(type_string):
              raise KeyError((
                  'Variable [{0:s}] is not of the correct type [{1:s}] for '
                  'this magic. Type is: {2!s}').format(
                      var_name, var_type, type(var_obj)))
          option_dict[key] = var_obj

    return_value = self.fn(**option_dict)
    state_obj = state.state()

    if not line_magic and variable:
      bind_to = variable

    return state_obj.set_output(
        output=return_value,
        magic_name=self.magic_name,
        bind_to=bind_to)

  def __dir__(self):
    options = getattr(self.argument_parser, '_option_string_actions', {})
    return list(options.keys())

  def __getattribute__(self, name: Text):
    # Overwriting function to behave like a function when called
    # by isinstance, in order to use the inspect module as well as to
    # produce a better help message.
    if name == '__class__':
      return types.FunctionType

    if name.startswith('func'):
      return self.fn.__getattribute__(name)  # pytype: disable=attribute-error

    return super(_Magic, self).__getattribute__(name)


def _get_arguments_from_arg_lines(
    arg_lines: List[Text]) -> List[Dict[Text, Text]]:
  """Return a list of parsed arguments from argument docstring.

  Args:
    arg_lines (list): a list of lines, one per argument as defined in
        the docstring.

  Returns:
    A list of dict, one per argument. Each dict will have the following
    attributes; variable, type and description.
  """
  args = []
  for arg_line in arg_lines:
    var_string, _, description = arg_line.partition(':')
    var, var_type = var_string.split()
    argument = {
        'variable': var,
        'type': var_type[1:-1],
        'description': description.strip()
    }
    args.append(argument)
  return args


def _get_argument_lines_from_docstring(lines: List[Text]) -> List[Text]:
  """Return names and types of arguments read from a doc string.

  This function takes in a function's docstring and returns back
  the argument section (Args:), with one line per argument defined.
  Arguments can be multi-lines.

  Args:
    lines (list): a list of lines read from a function's docstring.

  Returns:
    A list of lines that contain argument definitions.
  """
  arg_lines = []

  try:
    arg_index = [x.strip() for x in lines].index('Args:')
  except ValueError:
    return arg_lines

  new_index = arg_index + 1
  spaces = lines[arg_index].index('A')
  while True:
    line = lines[new_index]

    if not line.strip():
      break

    if line.strip() in ('Returns:', 'Raises:'):
      break

    # Checking indentation, whether the argument line is continuing or
    # a new argument is being defined.
    space_count = len(line) - len(line.lstrip(' '))
    if space_count == spaces * 2:
      arg_lines.append(line.strip())
    else:
      arg_lines[-1] = '{0:s} {1:s}'.format(arg_lines[-1], line.strip())

    new_index += 1
    if new_index >= len(lines)-1:
      break

  return arg_lines


def _add_function_arguments_to_parser(
    fn: MagicProtocol, parser: MagicArgumentParser):
  """Adds arguments to a parser from parsing a function.

  Args:
    fn (function): a function to extract an argument parser from.
    parser (MagicArgumentParser): an argument parser object, that will be used
        to add arguments to.

  Raises:
    ValueError: when the docstring is not correctly formatted.
  """
  try:
    doc_string_args = _parse_docstring(fn)
  except ValueError as e:
    raise ValueError(
        'Unable to register the magic %{0:s} since the docstring '
        'of the function is not correctly formatted. Error message '
        'is: {1!s}'.format(fn.__name__, e)) from e

  inspect_fn = inspect.getfullargspec

  try:
    spec = inspect_fn(fn)  # pytype: disable=wrong-arg-types
  except TypeError:
    spec = None

  if spec and spec.defaults:
    defaults_len = len(spec.defaults)
    default_values = dict(zip(spec.args[-defaults_len:], spec.defaults))
  else:
    default_values = {}

  for argument in doc_string_args:
    arg_type_string = argument.get('type', 'str')
    description = argument.get('description', '')
    # Percent sign has a special meaning for argument parser, escaping potential
    # percent signs in docstrings.
    description = description.replace('%', '%%')

    if argument.get('variable') == 'data':
      parser.storage['data'] = arg_type_string
      parser.storage['_data_help'] = description
      continue

    variable = argument.get('variable', '')
    arg_type = str
    if arg_type_string in ('str', 'unicode'):
      arg_type = str
    elif arg_type_string == 'float':
      arg_type = float
    elif arg_type_string == 'int':
      arg_type = int
    elif arg_type_string == 'bool':
      arg_type = bool
      arg_default = default_values.get(variable)
      if arg_default:
        action = 'store_false'
      else:
        action = 'store_true'
    else:
      # Type is a string reference to an object.
      arg_type = str
      parser.storage[variable] = arg_type_string

    if arg_type == bool:
      parser.add_argument(
          '--{0:s}'.format(variable), '-{0:s}'.format(variable),
          dest=variable, action=action,
          default=default_values.get(variable),
          help=description)
    else:
      parser.add_argument(
          '--{0:s}'.format(variable), '-{0:s}'.format(variable),
          dest=variable, type=arg_type, action='store',
          default=default_values.get(variable),
          help=description)


def _parse_docstring(function: MagicProtocol) -> List[Dict[Text, Text]]:
  """Return a list of arguments extracted from a function's docstring.

  Args:
    function (function): a function to extract the docstring from.

  Returns:
    A list of dict, one per argument. Each dict will have the following
    attributes; variable, type and description.
  """
  doc_string = getattr(function, '__doc__')
  if not doc_string:
    return []

  doc_lines = doc_string.split('\n')
  arg_lines = _get_argument_lines_from_docstring(doc_lines)
  return _get_arguments_from_arg_lines(arg_lines)


def _parse_line_string(line: Text) -> List[Text]:
  """Return a list of arguments from a line magic.

  Args:
    line (str): the value passed to the line magic, or line attribute in a
        cell magic.

  Returns:
    List of arguments that can be parsed by argparse.
  """
  arguments = []
  temp_args = []
  in_quotes = False
  arg_item = False
  quota_char = ''

  for item in line.strip().split():
    # Two cases to watch for, line starts with - (argument) or quotes.
    if in_quotes:
      if item[-1] == quota_char:
        temp_args.append(item[:-1])
        arguments.append(' '.join(temp_args))
        temp_args = []
        in_quotes = False
        quota_char = ''
      else:
        temp_args.append(item)
      continue

    if item[0] == '-':
      arguments.append(item)
      arg_item = True
      continue

    if item[0] in ('\'', '"'):
      quota_char = item[0]

      # The quoted argument is a single word.
      if item[-1] == quota_char:
        arguments.append(item[1:-1])
        quota_char = ''
        continue

      temp_args.append(item[1:])
      in_quotes = True
      quota_char = item[0]
      continue

    if arg_item:
      arguments.append(item)
      arg_item = False
    else:
      temp_args.append(item)

  if temp_args:
    arguments.append(' '.join(temp_args))

  return arguments


def picatrix_helper(function: Callable[..., Any]) -> Callable[..., Any]:
  """Decorator to register a picatrix helper.

  Args:
    function (function): if the decorator is called without any
        arguments the helper function is passed to the decorator.

  Returns:
   The function that was passed in.
  """
  typing_hints = typing.get_type_hints(function)
  manager.MagicManager.register_helper(
      name=function.__name__,
      helper=function,
      typing_help=typing_hints)

  try:
    _ = utils.ipython_get_global(function.__name__)
  except KeyError:
    utils.ipython_bind_global(function.__name__, function)

  return function


def picatrix_magic(
    function: Optional[MagicProtocol] = None,
    arguments: Optional[List[MagicArgument]] = None,
    name_func: Optional[Callable[[Text], Text]] = None,
    conditional: Optional[Callable[[None], bool]] = None) -> MagicProtocol:
  """Decorator to turn functions into IPYthon magics for picatrix.

  Args:
    function (function): if the decorator is called without any arguments
        the magic function is passed to the decorator.
    arguments (list): list of MagicArgument objects to pass to the magic
        argument parser.
    name_func (function: a name function that will accept a single argument
        and return back a name that will be used to register the magic.
        Optional and if not provide the name of tbe function will be used.
    conditional (function): a function that should return a bool, used to
        determine whether to register magic or not. This can be used by
        magics to determine whether a magic should be registered or not, for
        instance basing that on whether a certain magic is able to reach the
        service it requires. This is optional and if not provided a magic
        will be registered.

  Returns:
    the decorator function.
  """
  if function:
    magic_function = _Magic(
        function, name_func=name_func, arguments=arguments)
    manager.MagicManager.register_magic(magic_function, conditional)
    return magic_function

  def wrapper(func):
    """Wrapper for the magic."""
    magic_function = _Magic(
        func, name_func=name_func, arguments=arguments)

    manager.MagicManager.register_magic(magic_function, conditional)
    return magic_function

  return wrapper
