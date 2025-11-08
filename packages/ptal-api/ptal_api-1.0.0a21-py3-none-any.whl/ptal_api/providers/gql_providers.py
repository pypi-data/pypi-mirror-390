import logging
import time
from contextlib import AbstractContextManager
from typing import Optional

from jwt import decode
from keycloak import KeycloakOpenID
from sgqlc.endpoint.http import BaseEndpoint, HTTPEndpoint

logger = logging.getLogger(__name__)


def _configure_gql_client(
    uri: str, timeout: Optional[float] = None, _retries: int = 0, auth_token: Optional[str] = None
) -> HTTPEndpoint:
    headers = {"X-Auth-Token": auth_token, "Authorization": f"Bearer {auth_token}"} if auth_token is not None else None
    return HTTPEndpoint(uri, headers, timeout=timeout)


class AbstractGQLClient(AbstractContextManager):
    def __init__(self, gql_uri: str, timeout: float, retries: int, retry_timeout: float) -> None:
        super().__init__()
        self._gql_uri = gql_uri
        self._timeout = timeout
        self._retries = retries
        self._retry_timeout = retry_timeout
        self._gql_client: Optional[BaseEndpoint] = None

        if self._retries < 0:
            raise ValueError("Retries count cannot be negative")

    def execute(self, query, *args, **kwargs):
        for i in range(self._retries + 1):
            try:
                return self._gql_client.__call__(query, *args, **kwargs)
            except Exception as e:
                logger.exception(e)
                logger.error(f"Exception during executing {query}, retry...")
                if i == self._retries - 1:
                    raise e
                time.sleep(self._retry_timeout)
        return None


class NoAuthGQLClient(AbstractGQLClient):
    def __init__(self, gql_uri: str, timeout: float, retries: int, retry_timeout: float = 1) -> None:
        super().__init__(gql_uri, timeout, retries, retry_timeout)

    def __enter__(self):
        self._gql_client = _configure_gql_client(self._gql_uri, self._timeout, self._retries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._gql_client = None


class KeycloakAwareGQLClient(AbstractGQLClient):
    _TIME_OFFSET = 10  # in seconds

    def __init__(
        self,
        gql_uri: str,
        timeout: float,
        retries: int,
        auth_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        user: Optional[str] = None,
        pwd: Optional[str] = None,
        retry_timeout: float = 1,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        """
        Do not use basic constructor. Use create_with_user_pwd and create_with_token instead.

        Must be provided at least one of user and password or refresh token
        """

        if not (user and pwd or refresh_token):
            raise ValueError(
                "Authorization variables values are not set. "
                "Must be provided at least one of login and password or refresh token"
            )
        if any(env is None for env in (auth_url, realm, client_id, client_secret)):
            raise ValueError("Authorization variables values are not set")

        super().__init__(gql_uri, timeout, retries, retry_timeout)

        self._auth_url = auth_url
        self._realm = realm
        self._client_id = client_id
        self._client_secret = client_secret

        self._keycloak_openid: Optional[KeycloakOpenID] = None

        self._user: Optional[str] = user
        self._pwd: Optional[str] = pwd
        self._access_token: Optional[str] = access_token
        self._refresh_token: Optional[str] = refresh_token
        self._access_expiration_timestamp: Optional[float] = None
        self._refresh_expiration_timestamp: Optional[float] = None

        if access_token:
            self._access_expiration_timestamp = decode(access_token, options={"verify_signature": False})["exp"]
            self._gql_client = _configure_gql_client(self._gql_uri, self._timeout, self._retries, self._access_token)
        if refresh_token:
            self._refresh_expiration_timestamp = decode(refresh_token, options={"verify_signature": False})["exp"]
        elif not user:
            raise ValueError("Authorization variables values are not set")

    @classmethod
    def create_with_user_pwd(
        cls,
        gql_uri: str,
        timeout: float,
        retries: int,
        auth_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        user: str,
        pwd: str,
        retry_timeout: float = 1,
    ) -> "KeycloakAwareGQLClient":
        return KeycloakAwareGQLClient(
            gql_uri=gql_uri,
            timeout=timeout,
            retries=retries,
            auth_url=auth_url,
            realm=realm,
            client_id=client_id,
            client_secret=client_secret,
            user=user,
            pwd=pwd,
            retry_timeout=retry_timeout,
        )

    @classmethod
    def create_with_token(
        cls,
        gql_uri: str,
        timeout: float,
        retries: int,
        auth_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        access_token: Optional[str] = None,
        retry_timeout: float = 1,
    ) -> "KeycloakAwareGQLClient":
        return KeycloakAwareGQLClient(
            gql_uri=gql_uri,
            timeout=timeout,
            retries=retries,
            auth_url=auth_url,
            realm=realm,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            access_token=access_token,
            retry_timeout=retry_timeout,
        )

    def _ensure_session_liveness(self):
        offsetted_time = time.time() + self._TIME_OFFSET
        if self._access_expiration_timestamp is not None and offsetted_time < self._access_expiration_timestamp:
            return

        time_before_req = time.time()

        if self._refresh_expiration_timestamp is not None and offsetted_time < self._refresh_expiration_timestamp:
            logger.info("refreshing access token with refresh token")
            token_info = self._keycloak_openid.refresh_token(self._refresh_token)
        else:
            logger.info("refreshing access token with credentials")
            token_info = self._keycloak_openid.token(self._user, self._pwd)

        self._access_token = token_info["access_token"]
        self._access_expiration_timestamp = time_before_req + token_info["expires_in"]
        self._refresh_token = token_info["refresh_token"]
        self._refresh_expiration_timestamp = time_before_req + token_info["refresh_expires_in"]

        self._gql_client = _configure_gql_client(self._gql_uri, self._timeout, self._retries, self._access_token)

    def __enter__(self):
        self._keycloak_openid = KeycloakOpenID(self._auth_url, self._realm, self._client_id, self._client_secret)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._gql_client is not None:
            self._gql_client = None

        self._access_token, self._refresh_token = None, None
        self._access_expiration_timestamp, self._refresh_expiration_timestamp = None, None
        self._keycloak_openid, self._gql_client = None, None

    def execute(self, query, *args, **kwargs):
        self._ensure_session_liveness()
        return super().execute(query, *args, **kwargs)
