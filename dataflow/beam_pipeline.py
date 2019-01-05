
# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import argparse
import logging
import random

from past.builtins import unicode

import apache_beam as beam
from apache_beam import coders
from apache_beam.io import filebasedsource
from apache_beam.io import WriteToText
from apache_beam.io.iobase import Read
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.transforms import PTransform

import benepar
from benepar.spacy_plugin import BeneparComponent
from collections import namedtuple
from past2present import Sentence
import re
import spacy
import string


class BeneparExtension(object):
    """
    Represents a custom extension of a spacy Span with data from the
    `benepar` plugin. Allows access of properties using dot syntax.
    """
    def __init__(self, children=[], labels=[], parse_string=''):
        self.children = children
        self.labels = labels
        self.parse_string = parse_string

# BeneparExts = namedtuple('Extensions', ['children', 'labels', 'parse_string'])


class SpacyToken(object):
    """
    A pickleable version of a `spacy.tokens.token.Token` object. It holds a
    pointer to the `SpacySentenceSpan` object that represents the sentence
    in which it appears.
    """
    def __init__(self, sent, tok):
        self.sent = sent
        self.dep_ = tok.dep_
        self.i = tok.i
        self.lemma_ = tok.lemma_
        self.lower_ = tok.lower_
        self.pos_ = tok.pos_
        self.tag_ = tok.tag_
        self.text = tok.text
        self.text_with_ws = tok.text_with_ws
        self.whitespace_ = tok.whitespace_
        self.__children = [child.i for child in tok.children]
        self.__ancestors = [anc.i for anc in tok.ancestors]

    @property
    def children(self):
        for i in self.__children:
            yield self.sent[i - self.sent.start]

    @property
    def ancestors(self):
        for i in self.__ancestors:
            yield self.sent[i - self.sent.start]


class SpacySpan(object):
    """
    A pickleable version of a `spacy.tokens.span.Span` object. It requires
    the Berkeley Neural Parser `benepar` plugin, because it follows the
    constituency parse tree to transform each `spacy.tokens.span.Span` into
    a `SpacySpan`.
    """
    def __init__(self, sent, span=None):
        if span is None:
            self.sent = sent
            self.__len = 0
            self.text = ''
            self.text_with_ws = ''
            self.start = 0
            self.end = 0
            self._ = BeneparExtension(children=[], labels=[], parse_string='')
        else:
            chs = [SpacySpan(sent, child) for child in span._.children]
            ls = list(span._.labels)
            ps = span._.parse_string
            self.__len = len(span)
            self.sent = sent
            self.text = span.text
            self.text_with_ws = span.text_with_ws
            self.start = span.start
            self.end = span.end
            self._ = BeneparExtension(children=chs, labels=ls, parse_string=ps)

    def _relative_index(self, idx):
        if idx < 0:
            idx += self.__len
        idx += self.start - self.sent.start
        return idx

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = self.relative_index(slice.start)
            stop = self.relative_index(slice.stop)
            return self.sent[start:stop:slice.step]
        elif isinstance(key, int):
            return self.sent[self._relative_index(key)]
        else:
            raise ValueError('Index must be an integer or slice.')

    def __len__(self):
        return self.end - self.start


class SpacySentenceSpan(SpacySpan):
    """
    A pickleable version of a `spacy.tokens.span.Span` object that represents
    an entire sentence.

    A special type of span is required for this, because it needs to
    hold the tokens that other spans refer to.
    """
    def __init__(self, span):
        self.__tokens = [SpacyToken(self, tok) for tok in span]
        super(SpacySentenceSpan, self).__init__(self, span)

    def __getitem__(self, key):
        if isinstance(key, slice):
            if slice.step != 1:
                raise ValueError(
                        'Stepped slices are not supported in Span objects.')
            span = SpacySpan(self)

            start = self.relative_index(slice.start)
            stop = self.relative_index(slice.stop)

            if len(self.__tokens[start:stop]) == 0:
                return span
            print('start:', start, ' stop:', stop)
            all_but_last = map(lambda tok: tok.text_with_ws,
                               self.__tokens[start:stop - 1])
            last = self.__tokens[stop - 1]
            span.text = ''.join(all_but_last) + last.text
            span.text_with_ws = span.text + last.whitespace_
            return span
        elif isinstance(key, int):
            return self.sent.__tokens[self._relative_index(key)]
        else:
            raise ValueError('Index must be an integer or slice.')


class ParseWithSpacy(beam.DoFn):
    DEFAULT_BATCH_SIZE = 16
    DEFAULT_N_THREADS = 2
    MIN_SENTENCE_CHAR_LENGTH = 5

    def process(self, doc_string, *args, **kwargs):
        batch_size = (kwargs['batch_size'] if 'batch_size' in kwargs
                      else self.DEFAULT_BATCH_SIZE)
        n_threads = (kwargs['n_threads'] if 'n_threads' in kwargs
                     else self.DEFAULT_N_THREADS)
        doc_strings = [doc_string]
        docs = self.nlp.pipe(doc_strings,
                             batch_size=batch_size,
                             n_threads=n_threads)
        benepar = self.nlp.get_pipe('benepar')
        docs = map(benepar, docs)
        for doc in docs:
            for sent in doc.sents:
                if len(sent.text) >= 5:
                    yield SpacySentenceSpan(sent)

    def start_bundle(self):
        if not getattr(self, 'nlp', None):
            self.nlp = ParseWithSpacy.init_spacy_english_model()
        else:
            logging.debug('Spacy model already initialized.')

    @staticmethod
    def init_spacy_english_model():
        nlp = spacy.load('en_core_web_lg')
        nlp.add_pipe(BeneparComponent('benepar_en'))
        return nlp


class _GutenbergSource(filebasedsource.FileBasedSource):
    def __init__(self,
                 file_pattern,
                 chunk_char_length=4000):
        super(_GutenbergSource, self).__init__(file_pattern, splittable=False)
        self.chunk_char_length = chunk_char_length

    def read_records(self, file_name, range_tracker):
        start_offset = range_tracker.start_position()
        with self.open_file(file_name) as file_to_read:
            file_to_read.seek(start_offset)
            read_buffer = file_to_read.read()
            # Assume data is utf-8 starting with an optional BOM to be ignored.
            data = read_buffer.decode('utf-8-sig')
            data = _GutenbergSource.clean_text(data)
            for text in self.chunks(data):
                yield text

    @staticmethod
    def clean_text(text):
        """
        All non-ASCII characters must be removed for benepar `parse_string`
        to work.
        """
        # Replace carraige return and tab characters.
        text = text.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
        text = text.replace(u'\t', u' ')
        # Standardize quotes/apostrophes.
        text = re.sub(ur"[’‘]",  # noqa: E999
                      u"'",
                      re.sub(ur"[ ]*`", u"'", text))
        text = re.sub(ur'[“”]', u'"', text)
        # Standardize en/em-dashes.
        text = re.sub(ur'[–—]', u'-', text)
        # Replace non-ASCII characters with a space.
        text = re.sub(ur'[^\x00-\x7F]+', ' ', text)
        # Remove play character prompts like 'WALTER: ...'
        text = re.sub(ur"^[A-Z0-9'., ]+(?:\([^)]*\))?[:.][ ]*",  # noqa
                      u'',
                      text,
                      flags=re.M)
        # Remove titles which are lines with all-caps.
        text = re.sub(ur'^[A-Z0-9.,-?$#!;:\'’"_ ]+$', u'', text, flags=re.M)
        # Remove divider lines like '* * * * *' and antiquated punctuation.
        text = re.sub(
            ur'^[ ]*[-*=_].*[-*=_][ ]*$',
            u'',
            re.sub(u':--', u':', re.sub('&c', 'etc', text)),
            flags=re.M)
        # Remove leading spaces.
        text = re.sub(u'^[ ]+', u'', text)
        # Remove all line breaks except empty lines.
        text = re.sub(u'\n(?=[^\n])', u' ', text, flags=re.M)
        # Remove footnotes and references.
        # (they can be nested one deep: [Note [Note in note]])
        text = re.sub(  # noqa: W605
            ur'\[[^][]+\]', u'',
            re.sub(ur'\[[^][]+\]', '', re.sub(ur'^\[[^ ]+\] .*$', u'', text,
                                              flags=re.M)))
        # Remove underscores
        text = text.replace(u'_', u'')
        return text

    def chunks(self, text):
        """
        Newlines are kept in the text until this point so that we
        can be sure to cut off chunks at sentence breaks by cutting
        them off at the end of paragraphs.
        """
        remainder = text
        N = len(remainder)
        start = 0
        end = 0
        while start < N:
            end += self.chunk_char_length
            while end < N and remainder[end] != u'\n':
                end += 1
            # Remove all newlines and double spaces.
            yield re.sub(u' [ ]+',
                         u' ',
                         re.sub(u'\n',
                                u' ',
                                remainder[start:end]))
            start = end


class ReadGutenbergText(PTransform):
    def __init__(self,
                 file_pattern=None,
                 **kwargs):
        super(ReadGutenbergText, self).__init__(**kwargs)
        self._source = _GutenbergSource(file_pattern)

    def expand(self, pvalue):
        return pvalue.pipeline | Read(self._source)


def run(argv=None):
    """Main entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        default='gs://***REMOVED***/gutenberg/small/*.txt',
        help='Input file to process.')
    parser.add_argument(
        '--output',
        dest='output',
        default='gs://***REMOVED***/past2present/sentences',
        help='Output file to write results to.')
    parser.add_argument(
        '--cloud',
        action='store_true',
        help='Run the dataflow in the cloud.')
    known_args, pipeline_args = parser.parse_known_args(argv)

    if known_args.cloud:
        pipeline_args.append('--runner=DataflowRunner')
    else:
        pipeline_args.append('--runner=DirectRunner')

    n = random.randint(10000, 99999)
    pipeline_args.extend([
        '--job_name=past2present-%d' % n,
    ])
    print('Deploying job `past2present-%d`.' % n)

    pipeline_options = PipelineOptions(pipeline_args)
    # From https://github.com/apache/beam/blob/master/sdks/python/apache_beam
    #             /examples/complete/top_wikipedia_sessions.py :
    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options.view_as(SetupOptions).save_main_session = True

    def transform(sent):
        return (sent.text, Sentence(sent).transform_present())

    def format_result(before_after):
        (before, after) = before_after
        return u'< %s\n> %s' % (before, after)

    with beam.Pipeline(options=pipeline_options) as p:
        # Read the text file[pattern] into a PCollection.
        chunks = p | ReadGutenbergText(known_args.input)

        output = (
                chunks
                | 'Parse' >> beam.ParDo(ParseWithSpacy())
                | 'Transform' >> beam.Map(transform)
                | 'Format' >> beam.Map(format_result))

        output | WriteToText(known_args.output)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
