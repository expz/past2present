from beam_pipeline import SpacySentenceSpan, SpacySpan, SpacyToken
import pytest


@pytest.fixture
def nlp(scope='module'):
    import spacy
    from benepar.spacy_plugin import BeneparComponent
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(BeneparComponent('benepar_en'))
    return nlp


def test_parse(nlp):
    doc = nlp(u'The cat sat on the mat by a hat.')
    sent = next(doc.sents)
    psent = SpacySentenceSpan(sent)
    for child in psent._.children:
        assert isinstance(child, SpacySpan)
    s = [(sent, psent)]
    while s:
        span, pspan = s.pop()
        print('<', span.text)
        print('>', pspan.text)
        assert isinstance(pspan, SpacySpan)
        assert len(span) == len(pspan)
        assert span.text_with_ws == pspan.text_with_ws
        assert span.text == pspan.text
        if len(span) == 1:
            assert isinstance(pspan[0], SpacyToken)
            assert span[0].lemma_ == pspan[0].lemma_
            assert span[0].dep_ == pspan[0].dep_
            assert span[0].whitespace_ == pspan[0].whitespace_
        s.extend(reversed(list(zip(span._.children, pspan._.children))))
