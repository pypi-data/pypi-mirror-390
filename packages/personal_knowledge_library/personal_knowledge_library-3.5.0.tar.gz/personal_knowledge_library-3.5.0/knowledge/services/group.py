# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import urllib.parse
from typing import List, Any, Optional, Dict

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from knowledge.base.access import GroupAccessRight
from knowledge.base.ontology import NAME_TAG
from knowledge.services import (
    GROUP_USER_RIGHTS_TAG,
    DEFAULT_TIMEOUT,
    JOIN_KEY_PARAM,
    USER_TO_ADD_PARAM,
    USER_TO_REMOVE_PARAM,
    FORCE_PARAM,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
    USER_AGENT_HEADER_FLAG,
)
from knowledge.services.base import WacomServiceAPIClient, handle_error
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG

# -------------------------------------- Constant flags ----------------------------------------------------------------
from knowledge.services.users import User, FORCE_TAG, LIMIT_TAG, OFFSET_TAG


class Group:
    """
    Group
    -----
    In Personal Knowledge backend users can be logically grouped.

    Parameters
    ----------
    tenant_id: str
        Tenant id
    group_id: str
        Group id
    owner: str
        User id who has created the group.
    name: str
        Name of the group.
    join_key: str
        Key which is required to join the group
    rights: GroupAccessRight
        Access right for group

    Attributes
    ----------
    id: str
        Group identifier
    tenant_id: str
        Tenant identifier
    owner_id: str
        Owner identifier
    name: str
        Name of the group
    join_key: str
        Key which is required to join the group
    group_access_rights: GroupAccessRight
        Access rights for the group
    """

    def __init__(self, tenant_id: str, group_id: str, owner: str, name: str, join_key: str, rights: GroupAccessRight):
        self.__tenant_id: str = tenant_id
        self.__group_id: str = group_id
        self.__owner_id: str = owner
        self.__name: str = name
        self.__join_key: str = join_key
        self.__rights: GroupAccessRight = rights

    @property
    def id(self) -> str:
        """Group id."""
        return self.__group_id

    @property
    def tenant_id(self) -> str:
        """Tenant ID."""
        return self.__tenant_id

    @property
    def owner_id(self) -> Optional[str]:
        """Owner id (internal id) of the user, who owns the group."""
        return self.__owner_id

    @property
    def name(self) -> str:
        """Name of the group."""
        return self.__name

    @property
    def join_key(self) -> str:
        """Key for joining the group."""
        return self.__join_key

    @property
    def group_access_rights(self) -> GroupAccessRight:
        """Rights for group."""
        return self.__rights

    @classmethod
    def parse(cls, param: Dict[str, Any]) -> "Group":
        """Parse group from dictionary.

        Arguments
        ---------
        param: Dict[str, Any]
            Dictionary containing group information.

        Returns
        -------
        instance: Group
            The group object
        """
        tenant_id: str = param.get("tenantId")
        owner_id: str = param.get("ownerId")
        join_key: str = param.get("joinKey")
        group_id: str = param.get("id")
        name: str = param.get("name")
        rights: GroupAccessRight = GroupAccessRight.parse(param.get("groupUserRights", ["Read"]))
        return Group(
            tenant_id=tenant_id, group_id=group_id, owner=owner_id, join_key=join_key, name=name, rights=rights
        )

    def __repr__(self):
        return f"<Group: id:={self.id}, name:={self.name}, group access right:={self.group_access_rights}]>"


class GroupInfo(Group):
    """
    Group Information
    -----------------
    Provides additional information on the group.
    Users within the group are listed.

    Parameters
    ----------
    tenant_id: str
        Tenant id
    group_id: str
        Group id
    owner: str
        User id who has created the group.
    name: str
        Name of the group.
    join_key: str
        Key which is required to join the group
    rights: GroupAccessRight
        Access right for group
    group_users: List[User]
        List of users within the group.

    Attributes
    ----------
    group_users: List[User]
        List of all users that are part of the group.

    """

    def __init__(
        self,
        tenant_id: str,
        group_id: str,
        owner: str,
        name: str,
        join_key: str,
        rights: GroupAccessRight,
        group_users: List[User],
    ):
        self.__users: List[User] = group_users
        super().__init__(tenant_id, group_id, owner, name, join_key, rights)

    @property
    def group_users(self) -> List:
        """List of all users that are part of the group."""
        return self.__users

    @classmethod
    def parse(cls, param: Dict[str, Any]) -> "GroupInfo":
        tenant_id: str = param.get("tenantId")
        owner_id: str = param.get("ownerId")
        join_key: str = param.get("joinKey")
        group_id: str = param.get("id")
        name: str = param.get("name")
        rights: GroupAccessRight = GroupAccessRight.parse(param.get("groupUserRights", ["Read"]))
        return GroupInfo(
            tenant_id=tenant_id,
            group_id=group_id,
            owner=owner_id,
            join_key=join_key,
            name=name,
            rights=rights,
            group_users=[User.parse(u) for u in param.get("users", [])],
        )

    def __repr__(self):
        return (
            f"<GroupInfo: id:={self.id}, name:={self.name}, group access right:={self.group_access_rights}, "
            f"number of users:={len(self.group_users)}]>"
        )


class GroupManagementService(WacomServiceAPIClient):
    """
    Group Management Service API
    -----------------------------
    The service is managing groups.

    Functionality:
        - List all groups
        - Create group
        - Assign users to group
        - Share entities with group

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    GROUP_ENDPOINT: str = "group"
    """"Endpoint for all group related functionality."""

    def __init__(self, service_url: str = WacomServiceAPIClient.SERVICE_URL, service_endpoint: str = "graph/v1"):
        super().__init__("GroupManagementService", service_url=service_url, service_endpoint=service_endpoint)

    # ------------------------------------------ Groups handling ------------------------------------------------------

    def create_group(
        self,
        name: str,
        rights: GroupAccessRight = GroupAccessRight(read=True),
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Group:
        """
        Creates a group.

        Parameters
        ----------
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Returns
        -------
        group: Group
            Instance of the group.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        payload: Dict[str, str] = {NAME_TAG: name, GROUP_USER_RIGHTS_TAG: rights.to_list()}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                return Group.parse(response.json())
            raise handle_error("Creating of group failed.", response, payload=payload, headers=headers)

    def update_group(
        self,
        group_id: str,
        name: str,
        rights: GroupAccessRight = GroupAccessRight,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Updates a group.

        Parameters
        ----------
        group_id: str
            ID of the group.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        payload: Dict[str, str] = {NAME_TAG: name, GROUP_USER_RIGHTS_TAG: rights.to_list()}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.patch(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if not response.ok:
                raise handle_error("Update of group failed.", response, payload=payload, headers=headers)

    def delete_group(
        self,
        group_id: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Delete a group.

        Parameters
        ----------
        group_id: str
            ID of the group.
        force: bool (Default = False)
            If True, the group will be deleted even if it is not empty.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)

        Raises
        ------
        WacomServiceException
        If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        params: Dict[str, str] = {FORCE_TAG: str(force).lower()}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(
                url, headers=headers, params=params, verify=self.verify_calls, timeout=timeout
            )
            if not response.ok:
                raise handle_error("Deletion of group failed.", response, parameters=params, headers=headers)

    def listing_groups(
        self,
        admin: bool = False,
        limit: int = 20,
        offset: int = 0,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[Group]:
        """
        Listing all groups configured for this instance.

        Parameters
        ----------
        admin: bool (default:= False)
            Uses admin privilege to show all groups of the tenant.
            Requires user to have the role: TenantAdmin
        limit: int (default:= 20)
            Maximum number of groups to return.
        offset: int (default:= 0)
            Offset of the first group to return.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Returns
        -------
        user:  List[Groups]
            List of groups.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}"
        params: Dict[str, int] = {}
        if admin:
            url += "/admin"
            params[LIMIT_TAG] = limit
            params[OFFSET_TAG] = offset
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=params, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                groups: List[Dict[str, Any]] = response.json()
                return [Group.parse(g) for g in groups]
            raise handle_error("Listing of groups failed.", response, parameters=params, headers=headers)

    def group(
        self,
        group_id: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> GroupInfo:
        """Get a group.

        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Returns
        -------
        group: GroupInfo
            Instance of the group

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))

            response: Response = session.get(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if response.ok:
                group: Dict[str, Any] = response.json()
                return GroupInfo.parse(group)
            raise handle_error("Getting of group information failed.", response, headers=headers)

    def join_group(
        self,
        group_id: str,
        join_key: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """User joining a group with his auth token.

        Parameters
        ----------
        group_id: str
            Group ID
        join_key: str
            Key which is used to join the group.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/join"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        params: Dict[str, str] = {
            JOIN_KEY_PARAM: join_key,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, params=params, verify=self.verify_calls, timeout=timeout
            )
            if not response.ok:
                raise handle_error("Joining of group failed.", response, parameters=params, headers=headers)

    def leave_group(
        self,
        group_id: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """User leaving a group with his auth token.

        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/leave"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if not response.ok:
                raise handle_error("Leaving of group failed.", response, headers=headers)

    def add_user_to_group(
        self,
        group_id: str,
        user_id: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Adding a user to group.

        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is added to the group
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/user/add"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        params: Dict[str, str] = {
            USER_TO_ADD_PARAM: user_id,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = requests.post(
                url, headers=headers, params=params, verify=self.verify_calls, timeout=timeout
            )
            if not response.ok:
                raise handle_error("Adding of user to group failed.", response, parameters=params, headers=headers)

    def remove_user_from_group(
        self,
        group_id: str,
        user_id: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Remove a user from group.

        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is remove from the group
        force: bool
            If true remove user and entities owned by the user if any
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/user/remove"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        params: Dict[str, str] = {USER_TO_REMOVE_PARAM: user_id, FORCE_PARAM: force}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, params=params, verify=self.verify_calls, timeout=timeout
            )
            if not response.ok:
                raise handle_error("Removing of user from group failed.", response, parameters=params, headers=headers)

    def add_entity_to_group(
        self,
        group_id: str,
        entity_uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Adding an entity to group.

        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            Entity URI
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        uri: str = urllib.parse.quote(entity_uri)
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/entity/{uri}/add"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if not response.ok:
                raise handle_error("Adding of entity to group failed.", response, headers=headers)

    def remove_entity_to_group(
        self,
        group_id: str,
        entity_uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Remove an entity from group.

        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            URI of entity
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        uri: str = urllib.parse.quote(entity_uri)
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/entity/{uri}/remove"
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
            USER_AGENT_HEADER_FLAG: self.user_agent,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if not response.ok:
                raise handle_error("Removing of entity from group failed.", response, headers=headers)
