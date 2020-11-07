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
"""Initialization module for picatrix magics.

When starting a new notebook using picatrix it is enough to do

  from picatrix import notebook_init

  notebook_init.init()

And that would register magics and initialize the notebook to be able
to take advantage of picatrix magics and helper functions.
"""
# pylint: disable=unused-import
from picatrix import magics
from picatrix.lib import state


def init():
  """Initialize the notebook."""
  # Initialize the state object.
  _ = state.state()
