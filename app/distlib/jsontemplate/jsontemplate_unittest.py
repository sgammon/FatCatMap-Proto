#!/usr/bin/python -S
"""
jsontemplate_unittest.py
"""

__author__ = 'Andy Chu'


import os
import sys

if __name__ == '__main__':
  # for jsontemplate and pan, respectively
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pan.core import json
from pan.test import testy

# We need access to the internals here
from jsontemplate import _jsontemplate as jsontemplate
import verifier as python_verifier


class TokenizeTest(testy.Test):

  def testMakeTokenRegex(self):
    token_re = jsontemplate.MakeTokenRegex('[', ']')
    tokens = token_re.split("""
[# Comment#]

[# Comment !@#234 with all ...\\\ sorts of bad characters??]

[# Multi ]
[# Line ]
[# Comment ]
text
[!!]
text

[foo|fmt]
[bar|fmt]
""")
    self.verify.Equal(len(tokens), 17)

  def testSectionRegex(self):

    # Section names are required
    self.verify.Equal(
        jsontemplate._SECTION_RE.match('section'),
        None)
    self.verify.Equal(
        jsontemplate._SECTION_RE.match('repeated section'),
        None)

    self.verify.Equal(
        jsontemplate._SECTION_RE.match('section Foo').groups(),
        (None, 'Foo'))
    self.verify.Equal(
        jsontemplate._SECTION_RE.match('repeated section @').groups(),
        ('repeated', '@'))


class FromStringTest(testy.Test):

  def testEmpty(self):
    s = """\
Format-Char: |
Meta: <>
"""
    t = jsontemplate.FromString(s, _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], '')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], '|')

    # Empty template
    t = jsontemplate.FromString('', _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], '')
    self.verify.Equal(t.kwargs.get('meta'), None)
    self.verify.Equal(t.kwargs.get('format_char'), None)

  def testBadOptions(self):
    f = """\
Format-Char: |
Meta: <>
BAD STUFF
"""
    self.verify.Raises(
        jsontemplate.CompilationError, jsontemplate.FromString, f)

  def testTemplate(self):
    f = """\
format-char: :
meta: <>

Hello <there>
"""
    t = jsontemplate.FromString(f, _constructor=testy.ClassDef)
    self.verify.Equal(t.args[0], 'Hello <there>\n')
    self.verify.Equal(t.kwargs['meta'], '<>')
    self.verify.Equal(t.kwargs['format_char'], ':')

  def testNoOptions(self):
    # Bug fix
    f = """Hello {dude}"""
    t = jsontemplate.FromString(f)
    self.verify.Equal(t.expand({'dude': 'Andy'}), 'Hello Andy')




class InternalTemplateTest(testy.PyUnitCompatibleTest):
  """Tests that can only be run internally."""

  VERIFIERS = [python_verifier.InternalTemplateVerifier]

  def testFormatterRaisesException(self):

    # For now, integers can't be formatted directly as html.  Just omit the
    # formatter.
    t = jsontemplate.Template('There are {num|html} ways to do it')
    try:
      t.expand({'num': 5})
    except jsontemplate.EvaluationError, e:
      self.assert_(e.args[0].startswith('Formatting value 5'), e.args[0])
      self.assertEqual(e.original_exception.__class__, AttributeError)
    else:
      self.fail('Expected EvaluationError')

  def testMultipleFormatters(self):
    # TODO: This could have a version in the external test too, just not with
    # 'url-params', which is not the same across platforms because of dictionary
    # iteration order

    # Single formatter
    t = testy.ClassDef(
        'http://example.com?{params:url-params}',
        format_char=':')
    self.verify.Expansion(
        t,
        {'params': {'foo': 1, 'bar': 'String with spaces', 'baz': '!@#$%^&*('}},
        'http://example.com?baz=%21%40%23%24%25%5E%26%2A%28&foo=1&bar=String+with+spaces')

    # Multiple
    t = testy.ClassDef(
        'http://example.com?{params|url-params|html}',
        format_char='|')
    self.verify.Expansion(
        t,
        {'params': {'foo': 1, 'bar': 'String with spaces', 'baz': '!@#$%^&*('}},
        'http://example.com?baz=%21%40%23%24%25%5E%26%2A%28&amp;foo=1&amp;bar=String+with+spaces')

  def testExpandingDictionary(self):
    # This isn't strictly necessary, but it should make it easier for people to
    # develop templates iteratively.  They can see what the context is without
    # writing the whole template.

    def _More(format_str):
      if format_str == 'str':
        return lambda x: json.dumps(x, indent=2)
      else:
        return None

    t = testy.ClassDef('{@}', more_formatters=_More)
    d = {
        u'url': u'http://example.com',
        u'person': {
            u'name': u'Andy',
            u'age': 30,
            }
        }

    expected = """\
{
  "url": "http://example.com",
  "person": {
    "age": 30,
    "name": "Andy"
  }
}
"""
    # simplejson emits some extra whitespace
    self.verify.Expansion(t, d, expected, ignore_whitespace=True)

  def testScope(self):
    # From the wiki

    t = jsontemplate.Template("""
  {internal_link_prefix|htmltag}
  <p>
    <b>HTML Source</b>
    <ul>
      {.repeated section html-source-links}
        <p>
          <a
          href="{internal_link_prefix|htmltag}raw-html/data/wiki/columns-{num-cols}/{url-name}">
            {anchor|html}
          </a>
        <p>
      {.end}
    </ul>
  </p>
  """)
    d = {
        'internal_link_prefix': 'http://',
        'url-name': 'Wiki',
        'html-source-links': [
            {'num-cols': 1, 'anchor': '1'},
            {'num-cols': 2, 'anchor': '2'},
            ],
        }

    # Bug fix
    t.expand(d)

  #
  # Tests for public functions
  #

  def testExpand(self):
    """Test the free function expand."""
    self.verify.Equal(
        jsontemplate.expand('Hello {name}', {'name': 'World'}),
        'Hello World')

  def testTemplateExpand(self):
    t = jsontemplate.Template('Hello {name}')

    self.verify.Equal(
        t.expand({'name': 'World'}),
        'Hello World')

    # Test the kwarg syntax
    self.verify.Equal(
        t.expand(name='World'),
        'Hello World')

    # Only accepts one argument
    self.verify.Raises(TypeError, t.expand, {'name': 'world'}, 'extra')

  def testCompileTemplate(self):
    program = jsontemplate.CompileTemplate('{}')
    # If no builder is passed, them CompileTemplate should return a _Section
    # instance (the root of the program)
    self.assertEqual(type(program), jsontemplate._Section)

  def testSimpleUnicodeSubstitution(self):
    t = jsontemplate.Template(u'Hello {name}')

    self.verify.Equal(t.expand({u'name': u'World'}), u'Hello World')

    # TODO: Need a lot more comprehensive *external* unicode tests, as well as
    # ones for the internal API.  Need to test mixing of unicode() and str()
    # instances (or declare it undefined).


if __name__ == '__main__':
  testy.RunThisModule()
