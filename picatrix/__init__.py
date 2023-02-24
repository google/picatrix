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
"""Sets up Picatrix environment."""

from typing import Dict, Optional, Text, Tuple

import pandas as pd

from .lib.namespace import (
    AccessorNamespaceTemplate,
    FeatureContext,
    FeatureNamespace,
    Function,
    RootContext,
    RootNamespace,
)

px = RootNamespace(
    "px", """Picatrix root namespace.

    Features can be accessed as `px.{feature_name}`, e.g. `px.timesketch`.

    Try:
    * `px.search(\"keyword\")` to search features by keyword.
    * `px?` or `px.{feature_name}?` for help.
    """)
ctx = RootContext(
    "ctx", """Picatrix root context, holds all runtime parameters.

    To check runtime parameters of a certain feature, try `ctx.{feature_name}`,
    e.g. `ctx.timesketch.to_frame(with_values=True).

    Try:
    * `ctx.search(\"keyword\")` to search parameters by keyword
    * `ctx?` or `ctx.{feature_name}?` for help.
    """)


def new_namespace(
    name: Text,
    namespace_docstring: Optional[Text] = None,
    context_docstring: Optional[Text] = None,
) -> Tuple[FeatureNamespace, FeatureContext]:
  """Creates new Picatrix namespace and context for the feature.

  Newly registered feature will be available as:
  * `px.{name}` for functionalities,
  * `ctx.{name}` for runtime parameters, i.e. context.

  Args:
    name: new namespaces name
    namespace_docstring: custom docstring for the namespace
        if None, "`px.{name}` contains all Picatrix features of {name}"
    context_docstring: custom docstring for the context,
        if None, "`ctx.{name}` contains all Picatrix context for {name}"

  Returns:
    Tuple[FeatureNamespace, FeatureContext]: new namespace and context.

  Raises:
    NamespaceKeyExistsError: when namespace already exists
    NamespaceKeyError: when name is invalid, e.g. isn't Python identifier
  """
  return (
      px.add_namespace(name, docstring=namespace_docstring),
      ctx.add_namespace(name, docstring=context_docstring))


def new_line_magic(func: Function, name: Optional[Text] = None):
  """Adds new line magic to Picatrix namespace.

  Newly registered magic will be available as:
  * `%{name}` IPython line magic
  * `px.magic.{name}` function

  Args:
    func: function to be made into magic
    name: optional custom magic name, if None function name will be used

  Raises:
    NamespaceKeyExistsError: when required key already exists
    NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    MagicParsingError: when provided function is an invalid magic
  """
  px.add_line_magic(func, name)


def new_cell_magic(func: Function, name: Optional[Text] = None):
  """Adds new cell magic to Picatrix namespace.

  Newly registered magic will be available as:
  * `%%{name}` IPython cell magic
  * `px.magic.{name}` function

  Args:
    func: function to be made into magic
    name: optional custom magic name, if None function name will be used

  Raises:
    NamespaceKeyExistsError: when required key already exists
    NamespaceKeyError: when key is invalid, e.g. isn't Python identifier
    MagicParsingError: when provided function is an invalid magic
  """
  px.add_cell_magic(func, name if name else func.__name__)


_accessor_namespaces: Dict[Text, AccessorNamespaceTemplate] = {}


def new_accessor_namespace(
    name: Text, docstring: Optional[Text] = None) -> AccessorNamespaceTemplate:
  """Adds a new Pandas DataFrame accessor namespace.

  Function returns an AccessorNamespaceTemplate which exposes `.add` that
  can be used to add functions (accessors) to the namespace.
  Newly added namespace will later be available as <dataframe_obj>.<name>
  and its accessors as <dataframe_obj>.<name>.<accessor_name>.

  Args:
    name: name of the the namespace
    docstring: a string describing the functionalities of the namespace

  Returns:
    AccessorNamespaceTemplate: a template to be used for spawning accessor
      namespaces
  """
  if not docstring:
    docstring = f"Group of namespaces related to \"{name}\""

  template = AccessorNamespaceTemplate(docstring)
  reg = pd.api.extensions.register_dataframe_accessor  # type: ignore
  reg(name)(template.create)

  _accessor_namespaces[name] = template
  return template


# shouldn't be exported
del Dict, Optional, Text, Tuple
del AccessorNamespaceTemplate, FeatureContext, FeatureNamespace,
del Function, RootContext, RootNamespace
del pd
