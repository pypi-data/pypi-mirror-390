import pytest
from cli.tempspace import parse_time

def test_parse_time():
    assert parse_time("7d") == 168
    assert parse_time("24h") == 24
    assert parse_time("360") == 360
    assert parse_time("1D") == 24
    assert parse_time("2H") == 2
    assert parse_time(" 7d ") == 168
    assert parse_time("invalid") is None
    assert parse_time("1w") is None
