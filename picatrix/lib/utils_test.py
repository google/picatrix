# -*- coding: utf-8 -*-
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
"""Tests for the picatrix utils."""
import io

from picatrix.lib import utils


def test_asking_questions(monkeypatch):
  """Test the utils ask_question function.."""
  expected_answer = 'picatrix'
  monkeypatch.setattr('sys.stdin', io.StringIO(expected_answer))
  text = utils.ask_question('What is your name')
  assert text == expected_answer

  expected_answer = 234.12
  monkeypatch.setattr('sys.stdin', io.StringIO('234.12'))
  number = utils.ask_question('What is your number', input_type=float)
  assert number == expected_answer
