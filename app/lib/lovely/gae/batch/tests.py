##############################################################################
#
# Copyright 2009 Lovely Systems AG
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
#
##############################################################################

import os
import unittest, doctest

import lovely.gae.async.tests
from lovely.gae.testing import dbLayer
from zope.testing.doctestunit import DocFileSuite

def test_suite():
    readme = DocFileSuite(
        'README.txt', setUp=lovely.gae.async.tests.setUp,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        )
    s = unittest.TestSuite((readme,))
    s.layer=dbLayer
    return s
