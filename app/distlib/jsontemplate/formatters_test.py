#!/usr/bin/python -S
"""
formatters_test.py: Tests for formatters.py
"""

__author__ = 'Andy Chu'


import os
import sys
import unittest

if __name__ == '__main__':
  # for jsontemplate and pan, respectively
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from jsontemplate import formatters  # module under test
import jsontemplate

from pan.core import util
from pan.test import testy


class _CountedOpen(object):
  """Replacement for builtin open() that lets us count calls."""

  def __init__(self):
    self.open_count = 0

  def __call__(self, *args):
    filename = args[0]
    self.open_count += 1
    return open(*args)


class FormattersTest(testy.Test):

  def setUpOnce(self):

    # Constants used throughout this Test
    self.printf_template = '{a|printf %.2f}'
    self.include_template = '{profile|template-file include-test.jsont}'

    directory = os.path.join(os.path.dirname(__file__), 'testdata')
    self.include_formatter = formatters.TemplateFileInclude(directory)

  def setUp(self):

    # We want to reset the count to 0 on *every* test method
    self.saved = (formatters._open,)
    formatters._open = _CountedOpen()

    # Clear the cache on every test method
    formatters._compiled_template_cache = {}

  def tearDownOnce(self):
    (formatters._open,) = self.saved

  def testBasic(self):
    t = jsontemplate.Template('{a}')
    self.verify.Equal(t.expand(a=1), '1')

  def testPythonPercentFormat(self):
    t = jsontemplate.Template(
        self.printf_template, more_formatters=formatters.PythonPercentFormat)
    self.verify.Equal(t.expand(a=1.0/3), '0.33')

  def testTemplateInclude(self):
    t = jsontemplate.Template(
        self.include_template,
        more_formatters=self.include_formatter)

    d = {'profile': {'name': 'Bob', 'age': 13}}

    self.verify.Equal(t.expand(d), 'Bob is 13\n')

  def testTemplatesAreNotOpenedMoreThanOnce(self):
    t = jsontemplate.Template(
        """
        {profile1|template-file include-test.jsont}
        {profile2|template-file include-test.jsont}
        """,
        more_formatters=self.include_formatter)

    d = {
        'profile1': {'name': 'Bob', 'age': 13},
        'profile2': {'name': 'Andy', 'age': 80},
        }

    # Do the expansion ...
    t.expand(d)

    # .. and make sure that the include-test.jsont file wasn't opened more than
    # once
    self.verify.Equal(formatters._open.open_count, 1)

  def testLookupChain(self):
    chained = formatters.LookupChain([
        formatters.PythonPercentFormat,
        self.include_formatter,
        ])

    # Test that the cases from testPythonPercentFormat and testTemplateInclude
    # both work here.

    t = jsontemplate.Template(
        self.printf_template, more_formatters=chained)

    self.verify.Equal(t.expand(a=1.0/3), '0.33')

    t = jsontemplate.Template(
        self.include_template, more_formatters=chained)

    d = {'profile': {'name': 'Bob', 'age': 13}}

    self.verify.Equal(t.expand(d), 'Bob is 13\n')


if __name__ == '__main__':
  testy.RunThisModule()
