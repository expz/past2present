from past2present import transform_present


def test_transform_present_preserve_present():
    assert transform_present("The boy has been throwing and catching.",
                             True) == "The boy has been throwing and catching."
    assert transform_present("The boy would throw and catch the ball.",
                             True) == "The boy would throw and catch the ball."
    assert transform_present("The boy would have a ball for Christmas.",
                             True) == "The boy would have a ball for Christmas."
    assert transform_present('The boy has thrown and caught the ball.',
                             True) == 'The boy has thrown and caught the ball.'
    assert transform_present(
        "The boy hasn't thrown or caught the ball.",
        True) == "The boy hasn't thrown or caught the ball."
    assert transform_present(
        "The boy is throwing and catching the ball and catching it.",
        True) == "The boy is throwing and catching the ball and catching it."
    assert transform_present(
        "The ball is being thrown and caught by the boy.",
        True) == "The ball is being thrown and caught by the boy."
    assert transform_present(
        "The ball is thrown and caught by the boy.",
        True) == "The ball is thrown and caught by the boy."


def test_transform_present_preserve_future():
    assert transform_present("The boy will throw the ball and hit it.",
                             True) == "The boy will throw the ball and hit it."
    assert transform_present(
        "The boy will have thrown the ball before catching it.",
        True) == "The boy will have thrown the ball before catching it."
    assert transform_present(
        "The ball will have been thrown and caught by the boy.",
        True) == "The ball will have been thrown and caught by the boy."
    assert transform_present(
        "The boy will be throwing and catching the ball.",
        True) == "The boy will be throwing and catching the ball."
    assert transform_present(
        "The ball will be thrown and caught by the boy.",
        True) == "The ball will be thrown and caught by the boy."


def test_transform_present_conjunctions():
    assert transform_present("The boy threw the ball and hid.",
                             True) == "The boy throws the ball and hides."
    assert transform_present("The boy is going and was going.",
                             True) == "The boy is going and is going."
    assert transform_present("The boy did not walk but talked.",
                             True) == "The boy does not walk but talks."
    assert transform_present(
        "The boy walked but a mile talking with a friend.",
        True) == "The boy walks but a mile talking with a friend."
    assert transform_present(
        "The boy walked not even a mile before stopping.",
        True) == "The boy walks not even a mile before stopping."


def test_transform_present_complex():
    assert transform_present(
        "The boy has been throwing the ball that he bought at the store.",
        True) == "The boy has been throwing the ball that he buys at the store."
    assert transform_present(
        "The boy had been throwing the ball when it hit a window.",
        True) == "The boy has been throwing the ball when it hits a window."
    assert transform_present(
        "The boy has thrown the ball that hit a window.",
        True) == "The boy has thrown the ball that hits a window."
    assert transform_present(
        "The boy threw the ball which hit a window.",
        True) == "The boy throws the ball which hits a window."
    assert transform_present(
        "The boy threw the ball while the dog fetched it.",
        True) == "The boy throws the ball while the dog fetches it."
    assert transform_present(
        "The boy had thrown the ball, and it flew high.",
        True) == "The boy has thrown the ball, and it flies high."
    assert transform_present(
        "The boy dropped the ball while throwing it.",
        True) == "The boy drops the ball while throwing it."
    assert transform_present(
        "The boy was throwing the ball, but it kept falling to the ground.",
        True
    ) == "The boy is throwing the ball, but it keeps falling to the ground."
    assert transform_present(
        "Did the boy throw the ball that broke the window?",
        True) == "Does the boy throw the ball that breaks the window?"


def test_transform_present_past_tenses():
    assert transform_present('The boy threw the ball.',
                             True) == 'The boy throws the ball.'
    assert transform_present('The boy did throw the ball.',
                             True) == 'The boy does throw the ball.'

    assert transform_present("The boy didn't throw the ball.",
                             True) == "The boy doesn't throw the ball."
    assert transform_present("The boy did not throw the ball.",
                             True) == "The boy does not throw the ball."

    assert transform_present('The boy had thrown the ball.',
                             True) == 'The boy has thrown the ball.'
    assert transform_present('The boy was throwing the ball.',
                             True) == 'The boy is throwing the ball.'
    assert transform_present('The boy had been throwing the ball.',
                             True) == 'The boy has been throwing the ball.'

    assert transform_present("The boy hadn't thrown the ball.",
                             True) == "The boy hasn't thrown the ball."
    assert transform_present("The boy wasn't throwing the ball.",
                             True) == "The boy isn't throwing the ball."
    assert transform_present("The boy hadn't been throwing the ball.",
                             True) == "The boy hasn't been throwing the ball."

    assert transform_present('The boy would have thrown the ball.',
                             True) == 'The boy would throw the ball.'
    assert transform_present('The boy could have thrown the ball.',
                             True) == 'The boy could throw the ball.'
    assert transform_present('The boy must have thrown the ball.',
                             True) == 'The boy must throw the ball.'
    assert transform_present("The boy wouldn't have thrown the ball.",
                             True) == "The boy wouldn't throw the ball."

    assert transform_present('The ball was thrown by the boy.',
                             True) == 'The ball is thrown by the boy.'
    assert transform_present('The ball was being thrown by the boy.',
                             True) == 'The ball is being thrown by the boy.'
    assert transform_present("The ball wasn't being thrown by the boy.",
                             True) == "The ball isn't being thrown by the boy."
    assert transform_present('The ball would have been thrown by the boy.',
                             True) == 'The ball would be thrown by the boy.'
