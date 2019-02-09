from past2present import transform_present
import pytest
import spacy
from benepar.spacy_plugin import BeneparComponent


@pytest.fixture(scope="module")
def nlp():
    nlp = spacy.load('en_core_web_lg')
    nlp.add_pipe(BeneparComponent('benepar_en'))
    return nlp


def test_transform_present_preserve_present(nlp):
    assert transform_present(
        nlp, u"The girl has been throwing and catching.", True) == \
        u"The girl has been throwing and catching."
    assert transform_present(
        nlp, u"The girl would throw and catch the ball.", True) == \
        u"The girl would throw and catch the ball."
    assert transform_present(
        nlp, u"The girl would have a ball for Christmas.", True) == \
        u"The girl would have a ball for Christmas."
    assert transform_present(
        nlp, u'The girl has thrown and caught the ball.', True) == \
        u'The girl has thrown and caught the ball.'
    assert transform_present(
        nlp, u"The girl hasn't thrown or caught the ball.",
        True) == u"The girl hasn't thrown or caught the ball."
    assert transform_present(
        nlp, u"The girl is throwing and catching the ball and catching it.",
        True) == u"The girl is throwing and catching the ball and catching it."
    assert transform_present(
        nlp, u"The ball is being thrown and caught by the girl.",
        True) == u"The ball is being thrown and caught by the girl."
    assert transform_present(
        nlp, u"The ball is thrown and caught by the girl.",
        True) == u"The ball is thrown and caught by the girl."


def test_transform_present_preserve_future(nlp):
    assert transform_present(
        nlp, u"The girl will throw the ball and hit it.", True) == \
        u"The girl will throw the ball and hit it."
    assert transform_present(
        nlp, u"The girl will have thrown the ball before catching it.",
        True) == u"The girl will have thrown the ball before catching it."
    assert transform_present(
        nlp, u"The ball will have been thrown and caught by the girl.",
        True) == u"The ball will have been thrown and caught by the girl."
    assert transform_present(
        nlp, u"The girl will be throwing and catching the ball.",
        True) == u"The girl will be throwing and catching the ball."
    assert transform_present(
        nlp, u"The ball will be thrown and caught by the girl.",
        True) == u"The ball will be thrown and caught by the girl."


def test_transform_present_conjunctions(nlp):
    assert transform_present(nlp, u"The girl threw the ball and hid.",
                             True) == u"The girl throws the ball and hides."
    assert transform_present(nlp, u"The girl is going and was going.",
                             True) == u"The girl is going and is going."
    assert transform_present(nlp, u"The girl did not walk but talked.",
                             True) == u"The girl does not walk but talks."
    assert transform_present(
        nlp, u"The girl walked but a mile talking with a friend.",
        True) == u"The girl walks but a mile talking with a friend."
    assert transform_present(
        nlp, u"The girl walked not even a mile before stopping.",
        True) == u"The girl walks not even a mile before stopping."


def test_transform_present_complex(nlp):
    assert transform_present(
        nlp,
        u"The girl has been throwing the ball that he bought at the store.",
        True) == \
        u"The girl has been throwing the ball that he buys at the store."
    assert transform_present(
        nlp, u"The girl had been throwing the ball when it hit a window.",
        True) == u"The girl has been throwing the ball when it hits a window."
    assert transform_present(
        nlp, u"The girl has thrown the ball that hit a window.",
        True) == u"The girl has thrown the ball that hits a window."
    assert transform_present(
        nlp, u"The girl threw the ball which hit a window.",
        True) == u"The girl throws the ball which hits a window."
    assert transform_present(
        nlp, u"The girl threw the ball while the dog fetched it.",
        True) == u"The girl throws the ball while the dog fetches it."
    assert transform_present(
        nlp, u"The girl had thrown the ball, and it flew high.",
        True) == u"The girl has thrown the ball, and it flies high."
    assert transform_present(
        nlp, u"The girl dropped the ball while throwing it.",
        True) == u"The girl drops the ball while throwing it."
    assert transform_present(
        nlp,
        u"The girl was throwing the ball, but it kept falling to the ground.",
        True
    ) == u"The girl is throwing the ball, but it keeps falling to the ground."
    assert transform_present(
        nlp, u"Did the girl throw the ball that broke the window?",
        True) == u"Does the girl throw the ball that breaks the window?"


def test_transform_present_past_tenses(nlp):
    assert transform_present(nlp, u'The girl threw the ball.',
                             True) == u'The girl throws the ball.'
    assert transform_present(nlp, u'The girl did throw the ball.',
                             True) == u'The girl does throw the ball.'

    assert transform_present(nlp, u"The girl didn't throw the ball.",
                             True) == u"The girl doesn't throw the ball."
    assert transform_present(nlp, u"The girl did not throw the ball.",
                             True) == u"The girl does not throw the ball."

    assert transform_present(nlp, u'The girl had thrown the ball.',
                             True) == u'The girl has thrown the ball.'
    assert transform_present(nlp, u'The girl was throwing the ball.',
                             True) == u'The girl is throwing the ball.'
    assert transform_present(nlp, u'The girl had been throwing the ball.',
                             True) == u'The girl has been throwing the ball.'

    assert transform_present(nlp, u"The girl hadn't thrown the ball.",
                             True) == u"The girl hasn't thrown the ball."
    assert transform_present(nlp, u"The girl wasn't throwing the ball.",
                             True) == u"The girl isn't throwing the ball."
    assert transform_present(nlp, u"The girl hadn't been throwing the ball.",
                             True) == u"The girl hasn't been throwing the ball."

    assert transform_present(nlp, u'The girl would have thrown the ball.',
                             True) == u'The girl would throw the ball.'
    assert transform_present(nlp, u'The girl could have thrown the ball.',
                             True) == u'The girl could throw the ball.'
    assert transform_present(nlp, u'The girl must have thrown the ball.',
                             True) == u'The girl must throw the ball.'
    assert transform_present(nlp, u"The girl wouldn't have thrown the ball.",
                             True) == u"The girl wouldn't throw the ball."

    assert transform_present(nlp, u'The ball was thrown by the girl.',
                             True) == u'The ball is thrown by the girl.'
    assert transform_present(nlp, u'The ball was being thrown by the girl.',
                             True) == u'The ball is being thrown by the girl.'
    assert transform_present(
        nlp, u"The ball wasn't being thrown by the girl.", True) == \
        u"The ball isn't being thrown by the girl."
    assert transform_present(nlp,
                             u'The ball would have been thrown by the girl.',
                             True) == u'The ball would be thrown by the girl.'
