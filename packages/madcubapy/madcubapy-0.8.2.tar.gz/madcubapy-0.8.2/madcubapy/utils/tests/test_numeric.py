import pytest
from madcubapy.utils.numeric import _is_number

def test_numeric_strings():
    assert _is_number("34")
    assert _is_number("34.436712612874")

def test_invalid_strings():
    assert not _is_number("34s")
    assert not _is_number("34,342678")
    assert not _is_number("34 342678")
    assert not _is_number("number")
