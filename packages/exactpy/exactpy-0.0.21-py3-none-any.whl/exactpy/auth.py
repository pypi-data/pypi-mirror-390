import json
from pathlib import Path
from time import time
from typing import Callable, Tuple, Union
from urllib.parse import parse_qs, urlparse

from loguru import logger
from requests_oauthlib import OAuth2Session

from exactpy.exceptions import TokenRefreshError


class Auth:
    """Initializes the auth class that handles the Exact Online
    oauth authentication parts.

    Args:
        client_id (str): The Exact Online oauth client ID
        client_secret (str): The Exact Online oauth client secret
        auth_url (str): The oauth2 authentication url.
        token_url (str): The oauth2 token url.
        redirect_url (str): The redirect url, needs to match exactly what
            was entered in the app registration in the Exact Online portal.
        caching_enabled (bool): Whether cache callables should be called automatically. Defaults to True.
        cache_callable (Callable | None, optional): Callable to use for caching token info.
            Defaults to None. If set tot None, caching as well as cache loading will be
            disabled.
        cache_callable_kwargs (dict, optional): Keyword arguments to use for cache_callable.
            Defaults to {}.
        read_cache_callable (Callable | None, optional): Callable to use for loading cached token info.
            Defaults to None. If caching was disabled, loading cache won't happen either.
        read_cache_callable_kwargs (dict, optional): Keyword arguments to use for read_cache_callable.
            Defaults to {}.
        verbose (bool, optional): Whether to print verbose logs. Defaults to False.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        redirect_url: str,
        caching_enabled: bool = True,
        write_cache_callable: Callable | None = None,
        write_cache_callable_kwargs: dict = {},
        read_cache_callable: Callable | None = None,
        read_cache_callable_kwargs: dict = {},
        verbose: bool = False,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.redirect_url = redirect_url
        self.verbose = verbose
        self.token_info = {}
        self.caching_enabled = caching_enabled
        self.write_cache_callable = write_cache_callable
        self.write_cache_callable_kwargs = write_cache_callable_kwargs
        self.read_cache_callable = read_cache_callable
        self.read_cache_callable_kwargs = read_cache_callable_kwargs

        # Attempt to load token info
        if self.caching_enabled:
            if self.verbose:
                logger.info("Caching enabled. Attempting to load cache.")
            self.token_info = self.read_cache_callable(
                **self.read_cache_callable_kwargs
            )

    @staticmethod
    def write_cache(contents: dict, cache_path: Union[Path, str]):  # pragma: no cover
        """This is the default method for writing credentials.
        It serializes and saves a the received credential dict
        in string form to the given path.

        Args:
            contents (dict): The credentials dict.
            path (Union[Path, str]): The path to cache to.
        """
        path = Path(cache_path)
        with open(path, "w+") as fp:
            json.dump(contents, fp)

    @staticmethod
    def read_cache(cache_path: Union[Path, str]):  # pragma: no cover
        """This is the default method for reading credentials cache.
        It serializes and saves a the received credential dict
        in string form to the given path.

        Args:
            path (Union[Path, str]): The path to cache to.
        """
        cache_path = Path(cache_path)

        if not cache_path.exists():
            return
        with open(cache_path, "r") as fp:
            contents = json.load(fp)
        return contents

    @staticmethod
    def parse_response_url(response_url: str) -> Tuple[str, str]:
        """This method parses the response url received from
        Exact Online's oauth implementation and extracts both
        the code and the state query params, that can then
        be used to actually request and oauth token and
        refresh token.

        Args:
            response_url (str): The response that Exact Online
                redirected us to.

        Returns:
            Tuple[str, str]: A tuple containing code and state respectively.
        """
        parsed_url = urlparse(response_url)
        code = parse_qs(parsed_url.query)["code"][0]
        state = parse_qs(parsed_url.query)["state"][0]
        return code, state

    def get_authorization_url(self) -> str:  # pragma: no cover
        """Get Exact Online oauth authorization url that can be used to authorize
        the client to obtain a token.

        Returns:
            str: the authorization url.
        """
        oauth_session = OAuth2Session(self.client_id, redirect_uri=self.redirect_url)
        authorization_url, _ = oauth_session.authorization_url(self.auth_url)
        return authorization_url

    def acquire_token(self, redirect_response_url: str) -> None:  # pragma: no cover
        """Acquire token in a fresh state.

        Args:
            redirect_response_url (str): The response url after calling the authorization endpoint.
        """
        _, state = Auth.parse_response_url(redirect_response_url)
        oauth_session = OAuth2Session(
            client_id=self.client_id, state=state, redirect_uri=self.redirect_url
        )
        oauth_session.fetch_token(
            token_url=self.token_url,
            client_secret=self.client_secret,
            authorization_response=redirect_response_url,
        )

        self.token_info = {
            "access_token": oauth_session._client.access_token,
            "refresh_token": oauth_session._client.refresh_token,
            "expires_on": int(time() + float(oauth_session._client.expires_in)),
        }

        if self.caching_enabled:
            if self.verbose:
                logger.info("Caching enabled. Caching credentials.")
            self.write_cache_callable(
                contents=self.token_info, **self.write_cache_callable_kwargs
            )

    def refresh_token(self):  # pragma: no cover
        """Attempt to refresh oauth access token using the refresh token."""

        refresh_token = {
            "access_token": self.token_info["access_token"],
            "refresh_token": self.token_info["refresh_token"],
            "token_type": "Bearer",
            "expires_in": "-30",
        }

        oauth_session = OAuth2Session(client_id=self.client_id, token=refresh_token)

        try:
            oauth_session.refresh_token(
                token_url=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
            )

            self.token_info = {
                "access_token": oauth_session._client.access_token,
                "refresh_token": oauth_session._client.refresh_token,
                "expires_on": int(time() + float(oauth_session._client.expires_in)),
            }

            if self.caching_enabled:
                if self.verbose:
                    logger.info("Caching enabled. Caching credentials.")
                self.write_cache_callable(
                    contents=self.token_info, **self.write_cache_callable_kwargs
                )

        except Exception:
            raise TokenRefreshError(
                "Token could not be refreshed. Exception message: {e}"
            )

    def is_token_refresh_needed(self, now: float | None = None) -> bool:
        """Determines whether a token refresh is needed.

        Args:
            now (float, Optional): how soon is now?
                This is needed to be able to simulate expiration in
                unit tests. Defaults to None. In case it's None,
                it'll be set to time.time() in the method body.

        Returns:
            bool: whether a token refresh is needed
        """
        now = (now, time())[now is None]
        return self.token_info.get("expires_on", 0) - now < 30

    def _check_token_and_get_headers(self):
        """Performs token refresh if needed and returns bearer token header"""

        if self.is_token_refresh_needed():
            if self.verbose:
                logger.info("Token expired, refresh is needed.")
            self.refresh_token()

        return {"Authorization": f"Bearer {self.token_info['access_token']}"}
