# -*- coding: UTF-8 -*-

from beam_pipeline import _GutenbergSource


def test_convert_apostrophe():
    assert _GutenbergSource.clean_text(u"He said, 'Hello!'") == \
        u'He said, "Hello!"'
    assert _GutenbergSource.clean_text(u"'Hello!' he said.") == \
        u'"Hello!" he said.'
    assert _GutenbergSource.clean_text(u"He said, ‘Hello!’") == \
        u'He said, "Hello!"'
    assert _GutenbergSource.clean_text(u"‘Hello!’ he said.") == \
        u'"Hello!" he said.'
    assert _GutenbergSource.clean_text(u'He said, "Hello!"') == \
        u'He said, "Hello!"'
    assert _GutenbergSource.clean_text(u'"Hello!" he said.') == \
        u'"Hello!" he said.'
    assert _GutenbergSource.clean_text(
        u"He waved. ‘Goodbye,’ said he,") == \
        u'He waved. "Goodbye," said he,'
    assert _GutenbergSource.clean_text(
        u"‘If you will only listen,’ said") == \
        u'"If you will only listen," said'
    s1 = u"""‘Ah!’ said the young man,
‘that would be a great thing, but how can you contrive it?’

‘If you will only listen,’ said the fox"""
    s2 = (u'"Ah!" said the young man, "that would be a great thing, '
          + u'but how can you contrive it?"\n'
          + u'"If you will only listen," said the fox')
    assert _GutenbergSource.clean_text(s1) == s2
