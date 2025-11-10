from rustmodels import _rustmodels as rm
import pytest

@pytest.mark.parametrize("number", [
    '5', '238743289749823'
])
def test_is_numeric_true(number: str):
    value = rm._is_numeric(number) # pyright: ignore[reportPrivateUsage]
    assert value

@pytest.mark.parametrize("string", [
    'a', '16a', '!', 'njhwbds523?'
])
def test_is_numeric_false(string: str):
    value = rm._is_numeric('a') # pyright: ignore[reportPrivateUsage]
    assert not value
