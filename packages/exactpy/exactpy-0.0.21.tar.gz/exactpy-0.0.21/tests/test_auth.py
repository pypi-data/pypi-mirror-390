from time import time

import pytest

from exactpy.auth import Auth

CLIENT_ID = "some_id"
CLIENT_SECRET = "some_secret"
REDIRECT_URL = "https://www.some.uri"
AUTH_URL = "https://www.some.uri/oauth/auth"
TOKEN_URL = "https://www.some.uri/oauth/token"


@pytest.fixture
def auth_instance():
    inst = Auth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        auth_url=AUTH_URL,
        token_url=TOKEN_URL,
        redirect_url=REDIRECT_URL,
        caching_enabled=False,
        verbose=True,
    )

    inst.token_info = {
        "access_token": "some_token",
        "refresh_token": "refresh_token",
        "expires_on": time(),
    }

    return inst


@pytest.mark.parametrize(
    ("response_url", "expected_code", "expected_state"),
    [
        ("https://some_url?code=some_code&state=some_state", "some_code", "some_state"),
    ],
)
def test_parse_response_url(response_url: str, expected_code: str, expected_state: str):
    assert Auth.parse_response_url(response_url=response_url) == (
        expected_code,
        expected_state,
    )


@pytest.mark.parametrize(
    ("expires_on", "now", "expected_token_refresh_needed"),
    [
        (4102441200, 4102441200, True),
        (4102441200 + 10, 4102441200, True),
        (4102441200 + 31, 4102441200, False),
    ],
)
def test_is_token_refresh_needed(
    auth_instance: Auth,
    expires_on: float,
    now: float,
    expected_token_refresh_needed: str,
):
    auth_instance.token_info["expires_on"] = expires_on
    assert (
        auth_instance.is_token_refresh_needed(now=now) == expected_token_refresh_needed
    )
