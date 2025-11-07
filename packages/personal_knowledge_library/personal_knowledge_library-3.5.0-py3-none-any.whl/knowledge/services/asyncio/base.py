# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import asyncio
import json
import socket
import ssl
import sys
from datetime import datetime
from typing import Any, Tuple, Dict, Optional, Union

import aiohttp
import certifi
import orjson
from aiohttp import ClientTimeout
from cachetools import TTLCache

from knowledge import __version__, logger
from knowledge.services import (
    USER_AGENT_HEADER_FLAG,
    TENANT_API_KEY,
    CONTENT_TYPE_HEADER_FLAG,
    REFRESH_TOKEN_TAG,
    DEFAULT_TIMEOUT,
    EXPIRATION_DATE_TAG,
    ACCESS_TOKEN_TAG,
    APPLICATION_JSON_HEADER,
    EXTERNAL_USER_ID,
)
from knowledge.services.base import WacomServiceException, RESTAPIClient
from knowledge.services.session import TokenManager, PermanentSession, RefreshableSession, TimedSession

# A cache for storing DNS resolutions
dns_cache: TTLCache = TTLCache(maxsize=100, ttl=300)  # Adjust size and ttl as needed


async def cached_getaddrinfo(host: str, *args, **kwargs) -> Any:
    """
    Cached address information.

    Parameters
    ----------
    host: str
        Hostname
    args: Any
        Additional arguments
    kwargs: Any
        Additional keyword arguments

    Returns
    -------
    addr_info: Any
        Address information
    """
    if host in dns_cache:
        return dns_cache[host]
    addr_info = await asyncio.get_running_loop().getaddrinfo(host, port=None, *args, **kwargs)
    dns_cache[host] = addr_info
    return addr_info


class CachedResolver(aiohttp.resolver.AbstractResolver):
    """
    CachedResolver
    ==============
    Cached resolver for aiohttp.
    """

    async def close(self) -> None:
        pass

    async def resolve(self, host: str, port: int = 0, family: int = socket.AF_INET):
        infos = await cached_getaddrinfo(host)
        return [
            {
                "hostname": host,
                "host": info[4][0],
                "port": port,
                "family": family,
                "proto": 0,
                "flags": socket.AI_NUMERICHOST,
            }
            for info in infos
        ]


cached_resolver: CachedResolver = CachedResolver()
""" Cached resolver for aiohttp."""


async def handle_error(
    message: str,
    response: aiohttp.ClientResponse,
    parameters: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> WacomServiceException:
    """
    Handles an error response.

    Parameters
    ----------
    message: str
        Error message
    response: aiohttp.ClientResponse
        Response
    parameters: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    headers: Optional[Dict[str, str]] (Default:= None)
        Headers

    Returns
    -------
    WacomServiceException
        Create exception.
    """
    try:
        response_text: str = await response.text()
    except Exception as _:
        response_text: str = ""
    return WacomServiceException(
        message,
        method=response.method,
        url=response.url.human_repr(),
        params=parameters,
        payload=payload,
        headers=headers,
        status_code=response.status,
        service_response=response_text,
    )


class AsyncServiceAPIClient(RESTAPIClient):
    """
    Async Wacom Service API Client
    ------------------------------
    Abstract class for Wacom service APIs.

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    auth_service_endpoint: str (Default:= 'graph/v1')
        Authentication service endpoint
    verify_calls: bool (Default:= True)
        Flag if  API calls should be verified.

    """

    USER_ENDPOINT: str = "user"
    USER_LOGIN_ENDPOINT: str = f"{USER_ENDPOINT}/login"
    USER_REFRESH_ENDPOINT: str = f"{USER_ENDPOINT}/refresh"
    SERVICE_URL: str = "https://private-knowledge.wacom.com"
    """Production service URL"""
    STAGING_SERVICE_URL: str = "https://stage-private-knowledge.wacom.com"
    """Staging service URL"""

    def __init__(
        self,
        application_name: str = "Async Knowledge Client",
        service_url: str = SERVICE_URL,
        service_endpoint: str = "graph/v1",
        auth_service_endpoint: str = "graph/v1",
        verify_calls: bool = True,
        graceful_shutdown: bool = False,
    ):
        self.__service_endpoint: str = service_endpoint
        self.__auth_service_endpoint: str = auth_service_endpoint
        self.__application_name: str = application_name
        self.__token_manager: TokenManager = TokenManager()
        self.__current_session_id: Optional[str] = None
        self.__graceful_shutdown: bool = graceful_shutdown
        super().__init__(service_url, verify_calls)

    @property
    def application_name(self) -> str:
        """Application name."""
        return self.__application_name

    @property
    def user_agent(self) -> str:
        """User agent."""
        return (
            f"Personal Knowledge Library({self.application_name})/{__version__}"
            f"(+https://github.com/Wacom-Developer/personal-knowledge-library)"
        )

    @property
    def use_graceful_shutdown(self) -> bool:
        """Use graceful shutdown."""
        return self.__graceful_shutdown

    @property
    def current_session(self) -> Union[RefreshableSession, TimedSession, PermanentSession, None]:
        """Current session.

        Returns
        -------
        session: Union[TimedSession, RefreshableSession, PermanentSession]
            Current session

        Raises
        ------
        WacomServiceException
            Exception if no session is available.
        """
        if self.__current_session_id is None:
            raise WacomServiceException("No session set. Please login first.")
        session: Union[RefreshableSession, TimedSession, PermanentSession, None] = self.__token_manager.get_session(
            self.__current_session_id
        )
        if session is None:
            raise WacomServiceException(f"Unknown session id:= {self.__current_session_id}. Please login first.")
        return session

    async def use_session(self, session_id: str):
        """Use session.
        Parameters
        ----------
        session_id: str
            Session id
        """
        if self.__token_manager.has_session(session_id):
            self.__current_session_id = session_id
        else:
            raise WacomServiceException(f"Unknown session id:= {session_id}.")

    async def handle_token(self, force_refresh: bool = False, force_refresh_timeout: float = 120) -> Tuple[str, str]:
        """
        Handles the token and refreshes it if needed.

        Parameters
        ----------
        force_refresh: bool
            Force refresh token
        force_refresh_timeout: int
            Force refresh timeout
        Returns
        -------
        user_token: str
            The user token
        refresh_token: str
            The refresh token
        """
        # The session is not set
        if self.current_session is None:
            raise WacomServiceException("Authentication key is not set. Please login first.")

        # The token expired and is not refreshable
        if not self.current_session.refreshable and self.current_session.expired:
            raise WacomServiceException("Authentication key is expired and cannot be refreshed. Please login again.")

        # The token is not refreshable and the force refresh flag is set
        if not self.current_session.refreshable and force_refresh:
            raise WacomServiceException("Authentication key is not refreshable. Please login again.")

        # Refresh token if needed
        if self.current_session.refreshable and (
            self.current_session.expires_in < force_refresh_timeout or force_refresh
        ):
            try:
                auth_key, refresh_token, _ = await self.refresh_token(self.current_session.refresh_token)
            except WacomServiceException as e:
                if isinstance(self.current_session, PermanentSession):
                    permanent_session: PermanentSession = self.current_session
                    auth_key, refresh_token, _ = await self.request_user_token(
                        permanent_session.tenant_api_key, permanent_session.external_user_id
                    )
                else:
                    logger.error(f"Error refreshing token: {e}")
                    raise e
            self.current_session.update_session(auth_key, refresh_token)
            return auth_key, refresh_token
        return self.current_session.auth_token, self.current_session.refresh_token

    @staticmethod
    def __async_session__() -> aiohttp.ClientSession:
        """
        Returns an asynchronous session.

        Returns
        -------
        session: aiohttp.ClientSession
            Asynchronous session
        """
        timeout: ClientTimeout = ClientTimeout(total=DEFAULT_TIMEOUT)
        ssl_context: ssl.SSLContext = ssl.create_default_context(cafile=certifi.where())
        connector: aiohttp.TCPConnector = aiohttp.TCPConnector(ssl=ssl_context, resolver=cached_resolver)
        return aiohttp.ClientSession(
            json_serialize=lambda x: orjson.dumps(x).decode(), timeout=timeout, connector=connector
        )

    async def request_user_token(self, tenant_api_key: str, external_id: str) -> Tuple[str, str, datetime]:
        """
        Login as user by using the tenant key and its external user id.

        Parameters
        ----------
        tenant_api_key: str
            Tenant api key
        external_id: str
            External id.

        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: datatime
            Expiration time

        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.
        """
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            TENANT_API_KEY: tenant_api_key,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
        }
        payload: dict = {EXTERNAL_USER_ID: external_id}
        async with AsyncServiceAPIClient.__async_session__() as session:
            async with session.post(self.auth_endpoint, data=json.dumps(payload), headers=headers) as response:
                if response.ok:
                    response_token: Dict[str, str] = await response.json(loads=orjson.loads)
                    try:
                        date_object: datetime = datetime.fromisoformat(response_token[EXPIRATION_DATE_TAG])
                    except (TypeError, ValueError) as _:
                        date_object: datetime = datetime.now()
                        logger.warning(f"Parsing of expiration date failed. {response_token[EXPIRATION_DATE_TAG]}")
                else:
                    raise await handle_error("Login failed.", response, payload=payload, headers=headers)
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return response_token["accessToken"], response_token["refreshToken"], date_object

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str, datetime]:
        """
        Refreshing a token.

        Parameters
        ----------
        refresh_token: str
            Refresh token

        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: str
            Expiration time

        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.
        """
        url: str = f"{self.service_base_url}{AsyncServiceAPIClient.USER_REFRESH_ENDPOINT}/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: "application/json",
        }
        payload: Dict[str, str] = {REFRESH_TOKEN_TAG: refresh_token}
        async with self.__async_session__() as session:
            async with session.post(
                url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT, verify_ssl=self.verify_calls
            ) as response:
                if response.ok:
                    response_token: Dict[str, str] = await response.json()
                    timestamp_str_truncated: str = ""
                    try:
                        if sys.version_info <= (3, 10):
                            timestamp_str_truncated = response_token[EXPIRATION_DATE_TAG][:19] + "+00:00"
                        else:
                            timestamp_str_truncated = response_token[EXPIRATION_DATE_TAG]
                        date_object: datetime = datetime.fromisoformat(timestamp_str_truncated)
                    except (TypeError, ValueError) as _:
                        date_object: datetime = datetime.now()
                        logger.warning(f"Parsing of expiration date failed. {timestamp_str_truncated}")
                else:
                    raise await handle_error("Refresh of token failed.", response, payload=payload, headers=headers)
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return response_token[ACCESS_TOKEN_TAG], response_token[REFRESH_TOKEN_TAG], date_object

    async def login(self, tenant_api_key: str, external_user_id: str) -> PermanentSession:
        """Login as user by using the tenant id and its external user id.
        Parameters
        ----------
        tenant_api_key: str
            Tenant id
        external_user_id: str
            External user id
        Returns
        -------
        session: PermanentSession
            Session. The session is stored in the token manager and the client is using the session id for further
            calls.
        """
        auth_key, refresh_token, _ = await self.request_user_token(tenant_api_key, external_user_id)
        session: PermanentSession = self.__token_manager.add_session(
            auth_token=auth_key,
            refresh_token=refresh_token,
            tenant_api_key=tenant_api_key,
            external_user_id=external_user_id,
        )
        self.__current_session_id = session.id
        return session

    async def logout(self):
        """Logout user."""
        if self.__current_session_id:
            self.__token_manager.remove_session(self.__current_session_id)
        self.__current_session_id = None

    async def register_token(
        self, auth_key: str, refresh_token: Optional[str] = None
    ) -> Union[RefreshableSession, TimedSession]:
        """Register token.
        Parameters
        ----------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_token: str
            Refresh token

        Returns
        -------
        session: Union[RefreshableSession, TimedSession]
            Session. The session is stored in the token manager and the client is using the session id for further
            calls.
        """
        session = self.__token_manager.add_session(auth_token=auth_key, refresh_token=refresh_token)
        self.__current_session_id = session.id
        if isinstance(session, (RefreshableSession, TimedSession)):
            return session
        raise WacomServiceException(f"Wrong session type:= {type(session)}.")

    @property
    def service_endpoint(self):
        """Service endpoint."""
        return "" if len(self.__service_endpoint) == 0 else f"{self.__service_endpoint}/"

    @property
    def service_base_url(self):
        """Service endpoint."""
        return f"{self.service_url}/{self.service_endpoint}"

    @property
    def auth_endpoint(self) -> str:
        """Authentication endpoint."""
        # This is in graph service REST API
        return f"{self.service_url}/{self.__auth_service_endpoint}/{self.USER_LOGIN_ENDPOINT}"
