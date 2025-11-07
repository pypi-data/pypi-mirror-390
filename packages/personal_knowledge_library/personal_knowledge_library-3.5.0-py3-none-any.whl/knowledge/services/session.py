# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
"""
This module contains the session management.
There are three types of sessions:
    - **TimedSession**: The session is only valid until the token expires.
        There is no refresh token, thus the session cannot be refreshed.
    - **RefreshableSession**: The session is valid until the token expires.
        There is a refresh token, thus the session can be refreshed.
    - **PermanentSession**: The session is valid until the token expires.
        There is a refresh token, thus the session can be refreshed.
        Moreover, the session is bound to then _tenant api key_ and the _external user id_, which can be used to
        re-login when the refresh token expires.
"""
import hashlib
import logging
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Union, Optional, Dict, Any

import jwt

logger: logging.Logger = logging.getLogger(__name__)


class Session(ABC):
    """
    Session
    -------
    Abstract session class.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique session id, which will be the same for the same external user id, tenant,
        and instance of the service."""
        raise NotImplementedError

    @property
    @abstractmethod
    def auth_token(self) -> str:
        """Authentication key. The authentication key is used to identify an external user withing private knowledge."""
        raise NotImplementedError

    @property
    @abstractmethod
    def tenant_id(self) -> str:
        """Tenant id."""
        raise NotImplementedError

    @property
    def refresh_token(self) -> Optional[str]:
        """Refresh token. The refresh token is used to refresh the session."""
        return None

    @property
    @abstractmethod
    def refreshable(self) -> bool:
        """Is the session refreshable."""
        raise NotImplementedError

    @property
    @abstractmethod
    def expired(self) -> bool:
        """Is the session expired."""
        raise NotImplementedError

    @property
    @abstractmethod
    def expires_in(self) -> float:
        """Seconds until token is expired in seconds."""
        raise NotImplementedError

    @abstractmethod
    def update_session(self, auth_token: str, refresh_token: str):
        """
        Update the session.

        Parameters
        ----------
        auth_token: str
            The refreshed authentication token.
        refresh_token: str
            The refreshed refresh token.
        """
        raise NotImplementedError


class TimedSession(Session):
    """
    TimedSession
    ----------------
    The timed session is only valid until the token expires. There is no refresh token, thus the session cannot be
    refreshed.
    """

    def __init__(self, auth_token: str):
        self.__auth_token: str = auth_token
        self._auth_token_details_(auth_token)

    def _auth_token_details_(self, auth_token: str):
        """
        Extract the details from the authentication token.
        Parameters
        ----------
        auth_token: str
            Authentication token
        """
        structures: Dict[str, Any] = jwt.decode(auth_token, options={"verify_signature": False})
        if (
            "tenant" not in structures
            or "roles" not in structures
            or "exp" not in structures
            or "iss" not in structures
            or "ext-sub" not in structures
        ):
            raise ValueError("Invalid authentication token.")
        self.__tenant_id: str = structures["tenant"]
        self.__roles: str = structures["roles"]
        self.__timestamp: datetime = datetime.fromtimestamp(structures["exp"], tz=timezone.utc)
        self.__service_url: str = structures["iss"]
        self.__external_user_id: str = structures["ext-sub"]
        self.__id: str = TimedSession._session_id_(self.__service_url, self.__tenant_id, self.__external_user_id)

    @staticmethod
    def _session_id_(service_url: str, tenant_id: str, external_user_id: str):
        """
        Create a session id.

        Parameters
        ----------
        service_url: str
            Service url.
        tenant_id: str
            Tenant id.
        external_user_id: str
            External user id.

        Returns
        -------
        session_id: str
            Session id.
        """
        unique: str = f"{service_url}{tenant_id}{external_user_id}"
        return hashlib.sha256(unique.encode()).hexdigest()

    @staticmethod
    def extract_session_id(auth_key: str) -> str:
        """
        Extract the session id from the authentication key.
        Parameters
        ----------
        auth_key: str
            Authentication key.

        Returns
        -------
        session_id: str
            Session id.
        """
        structures: Dict[str, Any] = jwt.decode(auth_key, options={"verify_signature": False})
        if "ext-sub" not in structures:
            raise ValueError("Invalid authentication key.")
        service_url: str = structures["iss"]
        tenant_id: str = structures["tenant"]
        external_user_id: str = structures["ext-sub"]
        return TimedSession._session_id_(service_url, tenant_id, external_user_id)

    @property
    def tenant_id(self) -> str:
        """Tenant id."""
        return self.__tenant_id

    @property
    def roles(self) -> str:
        """Roles."""
        return self.__roles

    @property
    def service_url(self) -> str:
        """Service url."""
        return self.__service_url

    @property
    def external_user_id(self) -> str:
        """External user id."""
        return self.__external_user_id

    @property
    def expiration(self) -> datetime:
        """Timestamp when the token expires."""
        return self.__timestamp

    @property
    def auth_token(self) -> str:
        """JWT token for the session encoding the user id."""
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, value: str):
        self.__auth_token = value

    @property
    def id(self) -> str:
        """Session id."""
        return self.__id

    @property
    def expires_in(self) -> float:
        """Seconds until token is expired in seconds."""
        timestamp: datetime = datetime.now(tz=timezone.utc)
        return self.expiration.timestamp() - timestamp.timestamp()

    @property
    def expired(self) -> bool:
        """Is the session expired."""
        return self.expires_in <= 0.0

    @property
    def refreshable(self) -> bool:
        """Is the session refreshable."""
        return False

    def update_session(self, auth_token: str, refresh_token: str):
        raise NotImplementedError

    def __str__(self):
        return f"TimedSession(auth_token={self.auth_token})"


class RefreshableSession(TimedSession):
    """
    RefreshableSession
    ------------------
    The session class holds the information about the session.
    As there is refresh token, the session can be refreshed.
    """

    def __init__(self, auth_token: str, refresh_token: str):
        super().__init__(auth_token)
        self.__refresh_token: str = refresh_token

    @property
    def refresh_token(self) -> str:
        """Refresh token for the session."""
        return self.__refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str):
        self.__refresh_token = value

    def update_session(self, auth_token: str, refresh_token: str):
        """
        Refresh the session.
        Parameters
        ----------
        auth_token: str
            The refreshed authentication token.
        refresh_token: str
            The refreshed refresh token.
        """
        structures = jwt.decode(auth_token, options={"verify_signature": False})
        if (
            "tenant" not in structures
            or "roles" not in structures
            or "exp" not in structures
            or "iss" not in structures
            or "ext-sub" not in structures
        ):
            raise ValueError("Invalid authentication token.")
        if (
            self.tenant_id != structures["tenant"]
            or self.external_user_id != structures["ext-sub"]
            or self.service_url != structures["iss"]
        ):
            raise ValueError("The token is from a different user, tenant, or instance.")
        self._auth_token_details_(auth_token)
        self.auth_token = auth_token
        self.refresh_token = refresh_token

    @property
    def refreshable(self) -> bool:
        """Is the session refreshable."""
        return self.refresh_token is not None

    def __str__(self):
        return f"RefreshableSession(auth_token={self.auth_token}, refresh_token={self.refresh_token})"


class PermanentSession(RefreshableSession):
    """
    RefreshableSession
    ------------------
    The session class holds the information about the session.

    """

    def __init__(self, tenant_api_key: str, external_user_id: str, auth_token: str, refresh_token: str):
        super().__init__(auth_token, refresh_token)
        self.__tenant_api_key: str = tenant_api_key
        self.__external_user_id: str = external_user_id

    @property
    def tenant_api_key(self) -> str:
        """Tenant api key."""
        return self.__tenant_api_key

    @property
    def external_user_id(self) -> str:
        """External user id."""
        return self.__external_user_id

    def __str__(self):
        return (
            f"PermanentSession(tenant_api_key={self.tenant_api_key}, external_user_id={self.external_user_id}, "
            f"auth_token={self.auth_token}, refresh_token={self.refresh_token})"
        )


class TokenManager:
    """
    TokenManager
    ------------
    The token manager is a singleton that holds all the sessions for the users.
    """

    __instance: "TokenManager" = None
    __lock: threading.Lock = threading.Lock()  # Asynchronous lock for thread safety

    def __new__(cls):
        """Create a new singleton instance of the token manager."""
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super(TokenManager, cls).__new__(cls)
                cls.__instance.__initialize__()
        return cls.__instance

    def __initialize__(self):
        self.sessions: Dict[str, Union[TimedSession, RefreshableSession, PermanentSession]] = {}

    def add_session(
        self,
        auth_token: str,
        refresh_token: Optional[str] = None,
        tenant_api_key: Optional[str] = None,
        external_user_id: Optional[str] = None,
    ) -> Union[PermanentSession, RefreshableSession, TimedSession]:
        """
        Add a session.
        Parameters
        ----------
        auth_token: str
            The authentication token.
        refresh_token: Optional[str] [default := None]
            The refresh token.
        tenant_api_key: Optional[str] [default := None]
            The tenant api key.
        external_user_id: Optional[str] [default := None]
            The external user id.

        Returns
        -------
        session: Union[PermanentSession, RefreshableSession, TimedSession]
            The logged-in session.
        """
        with self.__lock:
            if tenant_api_key is not None and external_user_id is not None:
                session = PermanentSession(
                    tenant_api_key=tenant_api_key,
                    external_user_id=external_user_id,
                    auth_token=auth_token,
                    refresh_token=refresh_token,
                )
                # If there is a tenant api key and an external user id, then the session is permanent
            elif refresh_token is not None:
                session = RefreshableSession(auth_token=auth_token, refresh_token=refresh_token)
                # If there is a refresh token, then the session is refreshable
            else:
                session = TimedSession(auth_token=auth_token)
                # If there is no refresh token, then the session is timed
            if session.id in self.sessions:
                if type(session) is not type(self.sessions[session.id]):
                    logger.warning(
                        f"Session {session.id} already exists. "
                        f"Overwriting with new type of session {type(session)}, "
                        f"before {type(self.sessions[session.id])}."
                    )
                if not isinstance(self.sessions[session.id], type(session)):
                    logger.warning(
                        f"The session {session.id} is of a different type. "
                        f"Cached version is a {type(self.sessions[session.id])} "
                        f"and the new session is a {type(session)}."
                    )
            self.sessions[session.id] = session
            return session

    def get_session(self, session_id: str) -> Union[RefreshableSession, TimedSession, PermanentSession, None]:
        """
        Get a session by its id.

        Parameters
        ----------
        session_id: str
            Session id.

        Returns
        -------
        session: Union[RefreshableSession, TimedSession, PermanentSession]
            Depending on the session type, the session is returned.
        """
        with self.__lock:
            return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        """
        Remove a session by its id.

        Parameters
        ----------
        session_id: str
            Session id.
        """
        with self.__lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

    def has_session(self, session_id: str) -> bool:
        """
        Check if a session exists.

        Parameters
        ----------
        session_id: str
            Session id.

        Returns
        -------
        available: bool
            True if the session exists, otherwise False.
        """
        with self.__lock:
            return session_id in self.sessions
