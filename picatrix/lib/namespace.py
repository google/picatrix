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
"""Types and functions defining Picatrix namespacing."""

from difflib import get_close_matches
from inspect import cleandoc
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Text,
    Tuple,
    TypeVar,
    Union,
)

import pandas

from .error import Error
from .ipython import add_cell_magic, add_line_magic, delete_magic
from .magic import Magic, MagicType


class NamespaceKeyError(Error, KeyError):
  """Raised when Namespace attempted to operate on invalid key."""


class NamespaceKeyExistsError(NamespaceKeyError):
  """Raised when add operation was called on already existing key."""


class NamespaceKeyMissingError(NamespaceKeyError):
  """Raised when non-existing key is attempted to be accessed in a Namespace."""

  def __init__(self, key: Text, other_keys: Iterable[Text]):
    matches = get_close_matches(key, other_keys, 1)
    if not matches:
      super().__init__(f"{key} does not exist")
    else:
      super().__init__(
          f"{key} does not exist; "
          f"did you mean \"{matches[0]}\"")


A = TypeVar("A")  # pylint: disable=invalid-name


def _join_key(*args: Text):
  return ".".join(args)


def _as_df_record(name: Text, item: Any, with_doc: bool,
                  with_values: bool) -> Dict[Text, Text]:
  """Create a record compatible with pandas.DataFrame.from_records func.

  Args:
    name: human readable name of the item
    item: item to be translated into the row
    with_doc: if True, add whole docstring as a column; 1st line only otherwise

  Returns:
    Dict[Text, Text]: dictionary compatible with pandas.DataFrame.from_records
  """
  typ = "Namespace" if isinstance(item, Namespace) else str(type(item))
  doc = str(item.__doc__) if item.__doc__ else ""
  desc, *_ = doc.split("\n")

  record = {
      "Name": name,
      "Type": typ,
      "Description": desc,
  }

  if with_doc:
    record["Docstring"] = doc
  if with_values:
    record["Value"] = str(item)  # type: ignore

  return record


class Namespace(SimpleNamespace, Generic[A]):
  """Key-value type of structure with items accessible as attributes."""

  name: Text
  __dict__: Dict[Text, A]

  def __init__(self, name: Text, docstring: Text, **kwargs: A):
    super().__init__(**kwargs)
    self.__doc__ = cleandoc(docstring)
    self.name = name

  def __setattr__(self, key: Text, value: A):
    if not key.isidentifier():
      raise NamespaceKeyError(
          f"\"{key}\" isn't valid Python identifier, see: "
          "https://docs.python.org/3/reference/"
          "lexical_analysis.html#identifiers")
    elif key in self:
      raise NamespaceKeyExistsError(
          f"\"{key}\" already exists; remove it "
          "first with `del` operator, "
          f"e.g. `del {self.name}.{key}`")
    else:
      super().__setattr__(key, value)

  def __getattr__(self, key: Text) -> A:
    if key in self:
      return super().__getattr__(key)
    else:
      raise NamespaceKeyMissingError(key, self.keys())

  def __delattr__(self, key: Text):
    if key in self:
      return super().__delattr__(key)
    else:
      raise NamespaceKeyMissingError(key, self.keys())

  def __iter__(self) -> Iterator[Text]:
    return iter(self.__dict__)

  def __contains__(self, key: Text):
    return self.__dict__.__contains__(key)

  def keys(self) -> Iterator[Text]:
    """Iterator over all of the keys in the namespace."""
    return iter(self.__dict__.keys())

  def values(self) -> Iterator[A]:
    """Iterator over all of the values in the namespace."""
    return iter(self.__dict__.values())

  def items(self) -> Iterator[Tuple[Text, A]]:
    """Iterator over all of the key-value pairs in the namespace."""
    for key, value in self.__dict__.items():
      yield (key, value)

  def as_records(self,
                 with_doc: bool = False,
                 with_values: bool = False) -> List[Dict[Text, Text]]:
    """Make into records to be used with pandas.DataFrame.from_records func."""
    records = [_as_df_record(self.name, self, with_doc, False)]
    for key, value in self.items():
      if key == "name" or key.startswith("_"):
        continue

      if isinstance(value, Namespace):
        records.extend(value.as_records(with_doc, with_values))
      else:
        records.append(
            _as_df_record(
                _join_key(self.name, key), value, with_doc, with_values))
    return records

  def to_frame(
      self,
      with_doc: bool = False,
      with_values: bool = False) -> pandas.DataFrame:
    """Make namespace into pandas.DataFrame."""
    return pandas.DataFrame.from_records(  # type: ignore
        self.as_records(with_doc, with_values))

  def search(self, keyword: Text) -> pandas.DataFrame:
    """Search namespace for elements containing keyword."""
    df = self.to_frame(with_doc=True)
    return df[df.Name.str.contains(keyword) |  # type: ignore
              df.Docstring.str.contains(keyword)]  # type: ignore

  def _add(self, key: Text, value: A):
    """Adds a new value under the key.

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    """
    setattr(self, key, value)

  def get(self, key: Text, default: A) -> A:
    """Return the value for key if key is in the namespace, else default."""
    if key in self:
      return getattr(self, key)
    else:
      return default

  def delete(self, key: Text):
    """Deletes a key from the namespace."""
    self.__delattr__(key)


Function = Callable[..., Any]
"""Type representation of a function supported by Picatrix."""


class MagicNamespace(Namespace[Function]):
  """Namespace hosting IPython magics."""

  def __delattr__(self, key: Text):
    super().__delattr__(key)
    delete_magic(key)

  def add_line_magic(self, func: Function, name: Optional[Text] = None):
    """Adds new line magic (`%magic`) to the namespace.

    Args:
      func: function to be made into magic
      name: optional custom magic name, if None function name will be used

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
      MagicParsingError: when provided function is an invalid magic
    """
    name = name if name else func.__name__

    magic = Magic.wrap(MagicType.LINE, func, name=name)
    self._add(name, magic.func)

    add_line_magic(name, magic)

  def add_cell_magic(self, func: Function, name: Optional[Text] = None):
    """Adds new cell magic (`%%magic`) to the namespace.

    Args:
      func: function to be made into magic
      name: optional custom magic name, if None function name will be used

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
      MagicParsingError: when provided function is an invalid magic
    """
    name = name if name else func.__name__

    magic = Magic.wrap(MagicType.CELL, func, name=name)
    self._add(name, magic.func)

    add_cell_magic(name, magic)


class FeatureNamespace(Namespace[Function]):
  """Namespace hosting functionalities of the specific feature."""

  def add_function(self, func: Function, name: Optional[Text] = None):
    """Adds a new function to the namespace.

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    """
    if name is None:
      name = func.__name__
    self._add(name, func)


class RootNamespace(Namespace[Union[FeatureNamespace, Function]]):
  """Namespace hosting all Picatrix funcionalities."""

  magic: MagicNamespace

  def __init__(
      self, name: Text, docstring: Text, **kwargs: Union[FeatureNamespace,
                                                         Function]):
    super().__init__(name, docstring, **kwargs)
    self.magic = MagicNamespace(
        _join_key(self.name, "magic"),
        "Namespace holding all IPython magics registered by Picatrix.")

  def add_function(self, func: Function, name: Optional[Text] = None):
    """Adds a new function to the namespace.

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    """
    if name is None:
      name = func.__name__
    self._add(name, func)

  def add_line_magic(self, func: Function, name: Optional[Text] = None):
    """Adds new line magic (`%magic`) to the namespace.

    Args:
      func: function to be made into magic
      name: optional custom magic name, if None function name will be used

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
      MagicParsingError: when provided function is an invalid magic
    """
    self.magic.add_line_magic(func, name)

  def add_cell_magic(self, func: Function, name: Optional[Text] = None):
    """Adds new cell magic (`%%magic`) to the namespace.

    Args:
      func: function to be made into magic
      name: optional custom magic name, if None function name will be used

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
      MagicParsingError: when provided function is an invalid magic
    """
    self.magic.add_cell_magic(func, name)

  def add_namespace(
      self, name: Text, docstring: Optional[Text] = None) -> FeatureNamespace:
    """Adds a new namespace to the root namespace.

    Args:
      name: name of the new namespace
      docstring: optional docstring for the new namespace

    Returns:
      new namespace

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    """
    key = _join_key(self.name, name)
    if not docstring:
      docstring = f"`{key}` contains all Picatrix features of {name}"

    ns = FeatureNamespace(name=key, docstring=docstring)
    self._add(name, ns)
    return ns


class FeatureContext(Namespace[Any]):
  """Namespace hosting runtime parameters of the specific feature."""

  def add(self, key: Text, value: Any):
    """Adds a new value under the key.

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    """
    self._add(key, value)


class RootContext(Namespace[FeatureContext]):
  """Namespace hosting all Picatrix runtime parameters, i.e. context."""

  def add_namespace(
      self, name: Text, docstring: Optional[Text] = None) -> FeatureContext:
    """Adds a new context to the root context.

    Args:
      name: name of the new subcontext
      docstring: optional docstring for the new subcontext

    Returns:
      new subcontext

    Raises:
      NamespaceKeyExistsError: when required key already exists
      NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    """
    key = _join_key(self.name, name)
    if not docstring:
      docstring = f"`{key}` contains all Picatrix context for {name}"

    ctx = FeatureContext(name=key, docstring=docstring)
    self._add(name, ctx)
    return ctx
