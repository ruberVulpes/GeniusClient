import pytest

from genius_client import GeniusClient


def test_client_no_token():
    with pytest.raises(ValueError):
        GeniusClient()
