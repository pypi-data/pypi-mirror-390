from contextlib import contextmanager

import pytest


@contextmanager
def does_not_raise():
    yield


def raises_assertion_error():
    return pytest.raises(AssertionError)


def raises_exception(expected_exception):
    return lambda: pytest.raises(expected_exception)
