#!/usr/bin/python2.5
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
if '.' not in sys.path: sys.path.insert(0, '.')
if 'lib' not in sys.path: sys.path.insert(1, 'lib')
if 'distlib' not in sys.path: sys.path.insert(2, 'distlib')

try:
  from pipeline import *
except ImportError, e:
  import logging
  logging.warning(
      'Could not load Pipeline API. Will fix path for testing. %s: %s',
      e.__class__.__name__, str(e))
  import testutil
  testutil.fix_path()
  del logging
  from pipeline import *
