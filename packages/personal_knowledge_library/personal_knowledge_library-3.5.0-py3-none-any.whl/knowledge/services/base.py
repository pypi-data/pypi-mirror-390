# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import sys
from abc import ABC
from datetime import datetime
from typing import Any, Tuple, Dict, Optional, Union

import requests
from requests import Response

from knowledge import __version__, logger
from knowledge.services import DEFAULT_TIMEOUT
from knowledge.services import (
    USER_AGENT_HEADER_FLAG,
    TENANT_API_KEY,
    CONTENT_TYPE_HEADER_FLAG,
    REFRESH_TOKEN_TAG,
    EXPIRATION_DATE_TAG,
    ACCESS_TOKEN_TAG,
    APPLICATION_JSON_HEADER,
    EXTERNAL_USER_ID,
)
from knowledge.services.session import TokenManager, RefreshableSession, TimedSession, PermanentSession


class WacomServiceException(Exception):
    """Exception thrown if Wacom service fails.

    Parameters
    ----------
    message: str
        Error message
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    params: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    method: Optional[str] (Default:= None)
        Method
    url: Optional[str] (Default:= None)
        URL
    service_response: Optional[str] (Default:= None)
        Service response
    status_code: int (Default:= 500)
        Status code

    Attributes
    ----------
    headers: Optional[Dict[str, Any]]
        Headers of the exception
    method: Optional[str]
        Method of the exception
    params: Optional[Dict[str, Any]]
        Parameters of the exception
    payload: Optional[Dict[str, Any]]
        Payload of the exception
    url: Optional[str]
        URL of the exception
    message: str
        Message of the exception
    status_code: int
        Status code of the exception
    """

    def __init__(
        self,
        message: str,
        headers: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        method: Optional[str] = None,
        url: Optional[str] = None,
        service_response: Optional[str] = None,
        status_code: int = 500,
    ):
        super().__init__(message)
        self.__status_code: int = status_code
        self.__service_response: Optional[str] = service_response
        self.__message: str = message
        self.__headers: Optional[Dict[str, Any]] = headers
        self.__payload: Optional[Dict[str, Any]] = payload
        self.__params: Optional[Dict[str, Any]] = params
        self.__method: Optional[str] = method
        self.__url: Optional[str] = url

    @property
    def headers(self) -> Optional[Dict[str, Any]]:
        """Headers of the exception."""
        return self.__headers

    @property
    def method(self) -> Optional[str]:
        """Method of the exception."""
        return self.__method

    @property
    def params(self) -> Optional[Dict[str, Any]]:
        """Parameters of the exception."""
        return self.__params

    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        """Payload of the exception."""
        return self.__payload

    @property
    def url(self) -> Optional[str]:
        """URL of the exception."""
        return self.__url

    @property
    def message(self) -> str:
        """Message of the exception."""
        return self.__message

    @property
    def service_response(self) -> Optional[Response]:
        """Service response."""
        return self.__service_response

    @property
    def status_code(self) -> int:
        """Status code of the exception."""
        return self.__status_code


def format_exception(exception: WacomServiceException) -> str:
    """
    Formats the exception.

    Parameters
    ----------
    exception: WacomServiceException
        Exception

    Returns
    -------
    formatted_exception: str
        Formatted exception
    """
    return (
        f"WacomServiceException: {exception.message}\n"
        "--------------------------------------------------\n"
        f"URL:= {exception.url}\n,"
        f"method:= {exception.method}\n,"
        f"parameters:= {exception.params}\n,"
        f"payload:= {exception.payload}\n,"
        f"headers:= {exception.headers}\n,"
        f"status code=: {exception.status_code}\n,"
        f"service response:= {exception.service_response}"
    )


def handle_error(
    message: str,
    response: Response,
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
    response: Response
        Response from the service
    parameters: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    headers: Optional[Dict[str, str]] (Default:= None)
        Headers

    Returns
    -------
    WacomServiceException
        Returns the generated exception.
    """
    return WacomServiceException(
        message,
        url=response.url,
        method=response.request.method,
        params=parameters,
        payload=payload,
        headers=headers,
        status_code=response.status_code,
        service_response=response.text,
    )


class RESTAPIClient(ABC):
    """
    Abstract REST API client
    ------------------------
    REST API client handling the service url.

    Arguments
    ---------
    service_url: str
        Service URL for service
    verify_calls: bool (default:= False)
        Flag if the service calls should be verified
    """

    def __init__(self, service_url: str, verify_calls: bool = False):
        self.__service_url: str = service_url.rstrip("/")
        self.__verify_calls: bool = verify_calls

    @property
    def service_url(self) -> str:
        """Service URL."""
        return self.__service_url

    @property
    def verify_calls(self):
        """Certificate verification activated."""
        return self.__verify_calls

    @verify_calls.setter
    def verify_calls(self, value: bool):
        self.__verify_calls = value


class WacomServiceAPIClient(RESTAPIClient):
    """
    Wacom Service API Client
    ------------------------
    Abstract class for Wacom service APIs.

    Parameters
    ----------
    application_name: str
        Name of the application using the service
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
        application_name: str,
        service_url: str,
        service_endpoint: str,
        auth_service_endpoint: str = "graph/v1",
        verify_calls: bool = True,
    ):
        self.__application_name: str = application_name
        self.__service_endpoint: str = service_endpoint
        self.__auth_service_endpoint: str = auth_service_endpoint
        self.__token_manager: TokenManager = TokenManager()
        self.__current_session_id: Optional[str] = None
        super().__init__(service_url, verify_calls)

    @property
    def token_manager(self) -> TokenManager:
        """Token manager."""
        return self.__token_manager

    @property
    def auth_endpoint(self) -> str:
        """Authentication endpoint."""
        # This is in graph service REST API
        return f"{self.service_url}/{self.__auth_service_endpoint}/{self.USER_LOGIN_ENDPOINT}"

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

    def request_user_token(
        self, tenant_api_key: str, external_id: str, timeout: int = DEFAULT_TIMEOUT
    ) -> Tuple[str, str, datetime]:
        """
        Login as user by using the tenant key and its external user id.

        Parameters
        ----------
        tenant_api_key: str
            Tenant API key
        external_id: str
            External id.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.

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
        url: str = f"{self.auth_endpoint}"
        headers: dict = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            TENANT_API_KEY: tenant_api_key,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
        }
        payload: dict = {EXTERNAL_USER_ID: external_id}
        response: Response = requests.post(
            url, headers=headers, json=payload, timeout=timeout, verify=self.verify_calls, allow_redirects=True
        )
        if response.ok:
            try:
                response_token: Dict[str, str] = response.json()
                timestamp_str_truncated: str = ""
                try:
                    if sys.version_info <= (3, 10):
                        timestamp_str_truncated = response_token[EXPIRATION_DATE_TAG][:19] + "+00:00"
                    else:
                        timestamp_str_truncated = response_token[EXPIRATION_DATE_TAG]
                    date_object: datetime = datetime.fromisoformat(timestamp_str_truncated)
                except (TypeError, ValueError) as _:
                    date_object: datetime = datetime.now()
                    logger.warning(
                        f"Parsing of expiration date failed. {response_token[EXPIRATION_DATE_TAG]} "
                        f"-> {timestamp_str_truncated}"
                    )
                return response_token["accessToken"], response_token["refreshToken"], date_object
            except Exception as e:
                raise handle_error(f"Parsing of response failed. {e}", response) from e
        raise handle_error("User login failed.", response)

    def login(self, tenant_api_key: str, external_user_id: str) -> PermanentSession:
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
        auth_key, refresh_token, _ = self.request_user_token(tenant_api_key, external_user_id)
        session: PermanentSession = self.__token_manager.add_session(
            auth_token=auth_key,
            refresh_token=refresh_token,
            tenant_api_key=tenant_api_key,
            external_user_id=external_user_id,
        )
        self.__current_session_id = session.id
        return session

    def logout(self):
        """Logout user."""
        self.__current_session_id = None

    def register_token(
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

    def use_session(self, session_id: str):
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

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, datetime]:
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
        url: str = f"{self.service_base_url}{WacomServiceAPIClient.USER_REFRESH_ENDPOINT}/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
        }
        payload: Dict[str, str] = {REFRESH_TOKEN_TAG: refresh_token}
        response: Response = requests.post(
            url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT, verify=self.verify_calls
        )
        if response.ok:
            response_token: Dict[str, str] = response.json()
            try:
                date_object: datetime = datetime.fromisoformat(response_token[EXPIRATION_DATE_TAG])
            except (TypeError, ValueError) as _:
                date_object: datetime = datetime.now()
                logger.warning(f"Parsing of expiration date failed. {response_token[EXPIRATION_DATE_TAG]}")
            return response_token[ACCESS_TOKEN_TAG], response_token[REFRESH_TOKEN_TAG], date_object
        raise handle_error("Refreshing token failed.", response)

    def handle_token(self, force_refresh: bool = False, force_refresh_timeout: float = 120) -> Tuple[str, str]:
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
                auth_key, refresh_token, _ = self.refresh_token(self.current_session.refresh_token)
            except WacomServiceException as e:
                if isinstance(self.current_session, PermanentSession):
                    permanent_session: PermanentSession = self.current_session
                    auth_key, refresh_token, _ = self.request_user_token(
                        permanent_session.tenant_api_key, permanent_session.external_user_id
                    )
                else:
                    logger.error(f"Error refreshing token: {e}")
                    raise e
            self.current_session.update_session(auth_key, refresh_token)
            return auth_key, refresh_token
        return self.current_session.auth_token, self.current_session.refresh_token

    @property
    def user_agent(self) -> str:
        """User agent."""
        return (
            f"Personal Knowledge Library({self.application_name})/{__version__}"
            f"(+https://github.com/Wacom-Developer/personal-knowledge-library)"
        )

    @property
    def service_endpoint(self):
        """Service endpoint."""
        return "" if len(self.__service_endpoint) == 0 else f"{self.__service_endpoint}/"

    @property
    def service_base_url(self):
        """Service endpoint."""
        return f"{self.service_url}/{self.service_endpoint}"

    @property
    def application_name(self):
        """Application name."""
        return self.__application_name
