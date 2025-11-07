# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import enum
import gzip
import json
import os
import urllib
from pathlib import Path
from typing import Any, Optional, List, Dict, Tuple, Literal
from urllib.parse import urlparse

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from knowledge.base.entity import (
    DATA_PROPERTIES_TAG,
    TYPE_TAG,
    LABELS_TAG,
    RELATIONS_TAG,
    LOCALE_TAG,
    EntityStatus,
    Label,
    URIS_TAG,
    FORCE_TAG,
    URI_TAG,
    INCLUDE_RELATIONS_TAG,
)
from knowledge.base.language import LocaleCode
from knowledge.base.ontology import (
    DataProperty,
    OntologyPropertyReference,
    ThingObject,
    OntologyClassReference,
    ObjectProperty,
    EN_US,
)
from knowledge.base.response import JobStatus, ErrorLogResponse, NewEntityUrisResponse
from knowledge.services import (
    AUTHORIZATION_HEADER_FLAG,
    APPLICATION_JSON_HEADER,
    RELATION_TAG,
    TARGET,
    ACTIVATION_TAG,
    PREDICATE,
    OBJECT,
    SUBJECT,
    LIMIT_PARAMETER,
    ESTIMATE_COUNT,
    VISIBILITY_TAG,
    NEXT_PAGE_ID_TAG,
    LISTING,
    TOTAL_COUNT,
    SEARCH_TERM,
    LANGUAGE_PARAMETER,
    TYPES_PARAMETER,
    LIMIT,
    VALUE,
    LITERAL_PARAMETER,
    SEARCH_PATTERN_PARAMETER,
    SUBJECT_URI,
    RELATION_URI,
    OBJECT_URI,
    DEFAULT_TIMEOUT,
    IS_OWNER_PARAM,
    PRUNE_PARAM,
    STATUS_FORCE_LIST,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
    ENTITIES_TAG,
    NEL_PARAM,
    IndexType,
)
from knowledge.services.base import (
    WacomServiceAPIClient,
    WacomServiceException,
    USER_AGENT_HEADER_FLAG,
    CONTENT_TYPE_HEADER_FLAG,
    handle_error,
)
from knowledge.services.helper import split_updates, entity_payload
from knowledge.services.users import UserRole

MIME_TYPE: Dict[str, str] = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


# ------------------------------- Enum ---------------------------------------------------------------------------------
class SearchPattern(enum.Enum):
    """
    SearchPattern
    -------------
    Different search pattern for literal search.
    """

    REGEX = "regex"
    """Regular expression search pattern."""
    GT = "gt"
    """Greater than search pattern."""
    GTE = "gte"
    """Greater than or equal search pattern."""
    LT = "lt"
    """Less than search pattern."""
    LTE = "lte"
    """Less than or equal search pattern."""
    EQ = "eq"
    """Equal search pattern."""
    RANGE = "range"
    """Range search pattern."""


class Visibility(enum.Enum):
    """
    Visibility
    ----------
    Visibility of an entity.
    The visibility of an entity determines who can see the entity.
    """

    PRIVATE = "Private"
    """Only the owner of the entity can see the entity."""
    PUBLIC = "Public"
    """Everyone in the tenant can see the entity."""
    SHARED = "Shared"
    """Everyone who joined the group can see the entity."""


# -------------------------------------------- Service API Client ------------------------------------------------------
class WacomKnowledgeService(WacomServiceAPIClient):
    """
    WacomKnowledgeService
    ---------------------
    Client for the Semantic Ink Private knowledge system.

    Operations for entities:
        - Creation of entities
        - Update of entities
        - Deletion of entities
        - Listing of entities

    Parameters
    ----------
    application_name: str
        Name of the application using the service
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    USER_ENDPOINT: str = "user"
    ENTITY_ENDPOINT: str = "entity"
    ENTITY_BULK_ENDPOINT: str = "entity/bulk"
    ENTITY_IMAGE_ENDPOINT: str = "entity/image/"
    ACTIVATIONS_ENDPOINT: str = "entity/activations"
    LISTING_ENDPOINT: str = "entity/types"
    RELATION_ENDPOINT: str = "entity/{}/relation"
    RELATIONS_ENDPOINT: str = "entity/{}/relations"
    SEARCH_LABELS_ENDPOINT: str = "semantic-search/labels"
    SEARCH_TYPES_ENDPOINT: str = "semantic-search/types"
    SEARCH_LITERALS_ENDPOINT: str = "semantic-search/literal"
    SEARCH_DESCRIPTION_ENDPOINT: str = "semantic-search/description"
    SEARCH_RELATION_ENDPOINT: str = "semantic-search/relation"
    ONTOLOGY_UPDATE_ENDPOINT: str = "ontology-update"
    IMPORT_ENTITIES_ENDPOINT: str = "import"
    IMPORT_ERROR_LOG_ENDPOINT: str = "import/errorlog"
    REBUILD_VECTOR_SEARCH_INDEX: str = "vector-search/rebuild"
    REBUILD_NEL_INDEX: str = "nel/rebuild"

    def __init__(
        self,
        application_name: str = "Knowledge Client",
        service_url: str = WacomServiceAPIClient.SERVICE_URL,
        service_endpoint: str = "graph/v1",
    ):
        super().__init__(application_name, service_url, service_endpoint)

    def entity(
        self,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> ThingObject:
        """
        Retrieve entity information from personal knowledge, using the  URI as identifier.

        **Remark:** Object properties (relations) must be requested separately.

        Parameters
        ----------
        uri: str
            URI of entity
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Returns
        -------
        thing: ThingObject
            Entity with is type URI, description, an image/icon, and tags (labels).

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code or the entity is not found in the knowledge graph
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{uri}"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(url, headers=headers, timeout=timeout, verify=self.verify_calls)
            if response.ok:
                e: Dict[str, Any] = response.json()
                thing: ThingObject = ThingObject.from_dict(e)
                return thing
            raise handle_error(f"Retrieving of entity content failed. URI:={uri}.", response)

    def entities(
        self,
        uris: List[str],
        locale: Optional[LocaleCode] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[ThingObject]:
        """
        Retrieve entity information from personal knowledge, using the  URI as identifier.

        **Remark:** Object properties (relations) must be requested separately.

        Parameters
        ----------
        uris: List[str]
            List of URIs of entities
        locale: Optional[LocaleCode]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Returns
        -------
        things: List[ThingObject]
            Entities with is type URI, description, an image/icon, and tags (labels).

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code or the entity is not found in the knowledge graph
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {URIS_TAG: uris}
        if locale is not None:
            params[LOCALE_TAG] = locale
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, params=params, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                things: List[ThingObject] = []
                entities: List[Dict[str, Any]] = response.json()
                for e in entities:
                    thing: ThingObject = ThingObject.from_dict(e)
                    things.append(thing)
                return things
            raise handle_error(f"Retrieving of entity content failed. URIs:={uris}.", response)

    def delete_entities(
        self,
        uris: List[str],
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Delete a list of entities.

        Parameters
        ----------
        uris: List[str]
            List of URI of entities. **Remark:** More than 100 entities are not possible in one request
        force: bool
            Force deletion process
        auth_key: Optional[str] [default:= None]
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
            If the graph service returns an error code
        ValueError
            If more than 100 entities are given
        """
        if len(uris) > 100:
            raise ValueError("Please delete less than 100 entities.")
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {URIS_TAG: uris, FORCE_TAG: force}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(
                url, headers=headers, params=params, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error("Deletion of entities failed.", response)

    def delete_entity(
        self,
        uri: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Deletes an entity.

        Parameters
        ----------
        uri: str
            URI of entity
        force: bool
            Force deletion process
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
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{uri}"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(
                url, headers=headers, params={FORCE_TAG: force}, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error(f"Deletion of entity (URI:={uri}) failed.", response)

    def exists(
        self,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> bool:
        """
        Check if entity exists in knowledge graph.

        Parameters
        ----------
        uri: str -
            URI for entity
        auth_key: Optional[str]
            Auth key from user
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Returns
        -------
        flag: bool
            Flag if entity does exist
        """
        try:
            obj: ThingObject = self.entity(
                uri, auth_key=auth_key, timeout=timeout, max_retries=max_retries, backoff_factor=backoff_factor
            )
            return obj is not None
        except WacomServiceException:
            return False

    @staticmethod
    def __entity__(entity: ThingObject):
        return entity_payload(entity)

    def create_entity_bulk(
        self,
        entities: List[ThingObject],
        batch_size: int = 10,
        ignore_images: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[ThingObject]:
        """
        Creates entity in graph.

        Parameters
        ----------
        entities: List[ThingObject]
            Entities
        batch_size: int
            Batch size
        ignore_images: bool
            Ignore images
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds).
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)

        Returns
        -------
        things: List[ThingObject]
            List of entities with URI

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_BULK_ENDPOINT}"
        # Header info
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            payload: List[Dict[str, Any]] = [WacomKnowledgeService.__entity__(e) for e in entities]
            for bulk_idx in range(0, len(entities), batch_size):
                bulk = payload[bulk_idx : bulk_idx + batch_size]
                response: Response = session.post(
                    url, json=bulk, headers=headers, timeout=timeout, verify=self.verify_calls
                )
                if response.ok:
                    response_dict: Dict[str, Any] = response.json()

                    for idx, uri in enumerate(response_dict[URIS_TAG]):
                        if (
                            entities[bulk_idx + idx].image is not None
                            and entities[bulk_idx + idx].image != ""
                            and not ignore_images
                        ):
                            self.set_entity_image_url(uri, entities[bulk_idx + idx].image, auth_key=auth_key)
                        entities[bulk_idx + idx].uri = response_dict[URIS_TAG][idx]
                else:
                    raise handle_error("Pushing entity failed.", response)
        return entities

    def create_entity(
        self,
        entity: ThingObject,
        ignore_image: bool = False,
        auth_key: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> str:
        """
        Creates entity in graph.

        Parameters
        ----------
        entity: ThingObject
            Entity object that needs to be created
        ignore_image: bool [default:= False]
            Ignore image.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int [default:= 3]
            Maximum number of retries
        backoff_factor: float [default:= 0.1]
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        timeout: int [default:= 5]
            Timeout for the request
        Returns
        -------
        uri: str
            URI of entity

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}"
        # Header info
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        payload: Dict[str, Any] = WacomKnowledgeService.__entity__(entity)
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, json=payload, headers=headers, verify=self.verify_calls, timeout=timeout
            )

            if response.ok and not ignore_image:
                uri: str = response.json()[URI_TAG]
                # Set image
                try:
                    if entity.image is not None and entity.image.startswith("file:"):
                        p = urlparse(entity.image)
                        self.set_entity_image_local(uri, Path(p.path), auth_key=auth_key)
                    elif entity.image is not None and entity.image.startswith("/"):
                        self.set_entity_image_local(uri, Path(entity.image), auth_key=auth_key)
                    elif entity.image is not None and entity.image != "":
                        self.set_entity_image_url(uri, entity.image, auth_key=auth_key)
                except WacomServiceException as _:
                    pass
            if response.ok:
                uri: str = response.json()[URI_TAG]
                return uri
            raise handle_error("Pushing entity failed.", response)

    def update_entity(
        self,
        entity: ThingObject,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Updates entity in graph.

        Parameters
        ----------
        entity: ThingObject
            entity object
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
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        uri: str = entity.uri
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{uri}"
        # Header info
        headers: dict = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        payload: Dict[str, Any] = WacomKnowledgeService.__entity__(entity)
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.patch(
                url, json=payload, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error("Updating entity failed.", response)

    def add_entity_indexes(
        self,
        entity_uri: str,
        targets: List[IndexType],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[IndexType, Any]:
        """
        Updates index targets of an entity. The index targets can be set to "NEL", "ElasticSearch", "VectorSearchWord",
        or "VectorSearchDocument".
        If the target is already set for the entity, there will be no changes.

        Parameters
        ----------
        entity_uri: str
            URI of entity
        targets: List[Literal["NEL", "ElasticSearch", "VectorSearchWord", "VectorSearchDocument"]]
            List of indexing targets
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
        update_status: Dict[str, Any]
            Status per target (depending on the targets of entity and the ones set in the request). If the entity
            already has the target set, the status will be "Target already exists" for that target,
            otherwise it will be "UPSERT".

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{entity_uri}/indexes"
        # Header info
        headers: dict = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.patch(
                url, json=targets, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return response.json()
            raise handle_error("Updating entity indexes failed.", response)

    def remove_entity_indexes(
        self,
        entity_uri: str,
        targets: List[IndexType],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[IndexType, Any]:
        """
        Deletes the search index for a given entity.

        Parameters
        ----------
        entity_uri: str
            URI of entity
        targets: List[Literal["NEL", "ElasticSearch", "VectorSearchWord", "VectorSearchDocument"]]
            List of indexing targets
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
        update_status: Dict[str, Any]
            Status per target (depending on the targets of entity and the ones set in the request), e.g.,
            response will only contain {"NEL: "DELETE"}, if NEL is the only target in the request.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{entity_uri}/indexes"
        # Header info
        headers: dict = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(
                url, json=targets, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return response.json()
            raise handle_error("Deleting entity indexes failed.", response)

    def relations(
        self,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[OntologyPropertyReference, ObjectProperty]:
        """
        Retrieve the relations (object properties) of an entity.

        Parameters
        ----------
        uri: str
            Entity URI of the source
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)
        Returns
        -------
        relations: Dict[OntologyPropertyReference, ObjectProperty]
            All relations a dict

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{urllib.parse.quote(uri)}/relations"
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(url, headers=headers, timeout=timeout, verify=self.verify_calls)
            if response.ok:
                rel: list = response.json().get(RELATIONS_TAG)
                return ObjectProperty.create_from_list(rel)
            raise handle_error("Retrieving relations failed.", response)

    def labels(
        self,
        uri: str,
        locale: LocaleCode = EN_US,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[Label]:
        """
        Extract list labels of entity.

        Parameters
        ----------
        uri: str
            Entity URI of the source
        locale: LocaleCode  [default:= EN_US]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Returns
        -------
        labels: List[Label]
            List of labels of an entity.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{uri}/labels"
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount("https://", HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params={LOCALE_TAG: locale}, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                response_dict: dict = response.json()
                if LABELS_TAG in response_dict:
                    return [Label.create_from_dict(label) for label in response_dict[LABELS_TAG]]
                return []
            raise handle_error("Retrieving labels failed.", response)

    def literals(
        self,
        uri: str,
        locale: LocaleCode = EN_US,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[DataProperty]:
        """
        Collect all literals of entity.

        Parameters
        ----------
        uri: str
            Entity URI of the source
        locale: LocaleCode  [default:= EN_US]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1).

        Returns
        -------
        labels: List[DataProperty]
            List of data properties of an entity.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{uri}/literals"
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount("https://", HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params={LOCALE_TAG: locale}, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                literals: list = response.json().get(DATA_PROPERTIES_TAG)
                return DataProperty.create_from_list(literals)
            raise handle_error(f"Failed to pull literals for {uri}.", response)

    def create_relation(
        self,
        source: str,
        relation: OntologyPropertyReference,
        target: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Creates a relation for an entity to a source entity.

        Parameters
        ----------
        source: str
            Entity URI of the source
        relation: OntologyPropertyReference
            ObjectProperty property
        target: str
            Entity URI of the target
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{source}/relation"
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        params: dict = {RELATION_TAG: relation.iri, TARGET: target}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, params=params, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error("Creation of relation failed.", response)

    def create_relations_bulk(
        self,
        source: str,
        relations: Dict[OntologyPropertyReference, List[str]],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Creates all the relations for an entity to a source entity.

        Parameters
        ----------
        source: str
            Entity URI of the source
        relations: Dict[OntologyPropertyReference, List[str]]
            ObjectProperty property and targets mapping.
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{source}/relations"
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(
                total=max_retries, backoff_factor=backoff_factor, status_forcelist=[500, 502, 503, 504]
            )
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            for updates in split_updates(relations):
                response: Response = session.post(
                    url, timeout=timeout, json=updates, headers=headers, verify=self.verify_calls
                )
                if not response.ok:
                    raise handle_error("Creation of relation failed.", response, payload=updates)

    def remove_relation(
        self,
        source: str,
        relation: OntologyPropertyReference,
        target: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Removes a relation.

        Parameters
        ----------
        source: str
            Entity uri of the source
        relation: OntologyPropertyReference
            ObjectProperty property
        target: str
            Entity uri of the target
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ENTITY_ENDPOINT}/{source}/relation"
        params: Dict[str, str] = {RELATION_TAG: relation.iri, TARGET: target}
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            # Get response
            response: Response = session.delete(
                url, params=params, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error("Removal of relation failed.", response)

    def activations(
        self,
        uris: List[str],
        depth: int,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[Dict[str, ThingObject], List[Tuple[str, OntologyPropertyReference, str]]]:
        """
        Spreading activation, retrieving the entities related to an entity.

        Parameters
        ----------
        uris: List[str]
            List of URIS for entity.
        depth: int
            Depth of activations
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay) (default: 0.1)

        Returns
        -------
        entity_map: Dict[str, ThingObject]
            Map with entity and its URI as key.
        relations: List[Tuple[str, OntologyPropertyReference, str]]
            List of relations with subject predicate, (Property), and subject

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code, and activation failed.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.ACTIVATIONS_ENDPOINT}"

        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: dict = {URIS_TAG: uris, ACTIVATION_TAG: depth}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=params, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                entities: Dict[str, Any] = response.json()
                things: Dict[str, ThingObject] = {e[URI_TAG]: ThingObject.from_dict(e) for e in entities[ENTITIES_TAG]}
                relations: List[Tuple[str, OntologyPropertyReference, str]] = []
                for r in entities[RELATIONS_TAG]:
                    relation: OntologyPropertyReference = OntologyPropertyReference.parse(r[PREDICATE])
                    relations.append((r[SUBJECT], relation, r[OBJECT]))
                    if r[SUBJECT] in things:
                        things[r[SUBJECT]].add_relation(ObjectProperty(relation, outgoing=[r[OBJECT]]))
                return things, relations
        raise handle_error(f"Activation failed. uris:= {uris} activation:={depth}).", response)

    def listing(
        self,
        filter_type: OntologyClassReference,
        page_id: Optional[str] = None,
        limit: int = 30,
        locale: Optional[LocaleCode] = None,
        visibility: Optional[Visibility] = None,
        is_owner: Optional[bool] = None,
        estimate_count: bool = False,
        include_relations: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[List[ThingObject], int, str]:
        """
        List all entities visible to users.

        Parameters
        ----------
        filter_type: OntologyClassReference
            Filtering with entity
        page_id: Optional[str]
            Page id. Start from this page id
        limit: int
            Limit of the returned entities.
        locale: Optional[LanguageCode] = [default:=None]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        visibility: Optional[Visibility] [default:=None]
            Filter the entities based on its visibilities
        is_owner: Optional[bool] = [default:=None]
            Filter the entities based on its owner
        estimate_count: bool = [default:=False]
            Request an estimate of the entities in a tenant.
        include_relations: bool = [default:=False]
            Include relations in the response.
        auth_key: Optional[str] = [default:=None]
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
        entities: List[ThingObject]
            List of entities
        estimated_total_number: int
            Number of all entities
        next_page_id: str
            Identifier of the next page

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.LISTING_ENDPOINT}"
        # Header with auth token
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        # Parameter with filtering and limit
        parameters: Dict[str, Any] = {TYPE_TAG: filter_type.iri, LIMIT_PARAMETER: limit, ESTIMATE_COUNT: estimate_count}
        if locale:
            parameters[LOCALE_TAG] = locale
        if visibility:
            parameters[VISIBILITY_TAG] = str(visibility.value)
        if is_owner:
            parameters[IS_OWNER_PARAM] = str(is_owner)
        # If filtering is configured
        if page_id:
            parameters[NEXT_PAGE_ID_TAG] = page_id
        if include_relations:
            parameters[INCLUDE_RELATIONS_TAG] = str(include_relations)
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            # Send request
            response: Response = session.get(
                url, params=parameters, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            # If response is successful
            if response.ok:
                entities_resp: dict = response.json()
                next_page_id: str = entities_resp[NEXT_PAGE_ID_TAG]
                estimated_total_number: int = entities_resp.get(TOTAL_COUNT, 0)
                entities: List[ThingObject] = []
                if LISTING in entities_resp:
                    for e in entities_resp[LISTING]:
                        thing: ThingObject = ThingObject.from_dict(e)
                        thing.status_flag = EntityStatus.SYNCED
                        entities.append(thing)
                return entities, estimated_total_number, next_page_id
        raise handle_error(f"Failed to list the entities (since:= {page_id}, limit:={limit}).", response)

    def search_all(
        self,
        search_term: str,
        language_code: LocaleCode,
        types: List[OntologyClassReference],
        limit: int = 30,
        next_page_id: str = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[List[ThingObject], str]:
        """Search term in labels, literals and description.

        Parameters
        ----------
        auth_key: str
            Auth key from user
        search_term: str
            Search term.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        types: List[OntologyClassReference]
            Limits the types for search.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str (default:=None)
            ID of the next page within pagination.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)

        Returns
        -------
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        parameters: Dict[str, Any] = {
            SEARCH_TERM: search_term,
            LANGUAGE_PARAMETER: language_code,
            TYPES_PARAMETER: [ot.iri for ot in types],
            LIMIT: limit,
            NEXT_PAGE_ID_TAG: next_page_id,
        }
        url: str = f"{self.service_base_url}{WacomKnowledgeService.SEARCH_TYPES_ENDPOINT}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=parameters, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return WacomKnowledgeService.__search_results__(response.json())
            raise handle_error(f"Search on labels {search_term} failed. ", response)

    def search_labels(
        self,
        search_term: str,
        language_code: LocaleCode,
        limit: int = 30,
        next_page_id: str = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[List[ThingObject], str]:
        """Search for matches in labels.

        Parameters
        ----------
        search_term: str
            Search term.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str (default:=None)
            ID of the next page within pagination.
        auth_key: Optional[str] = None
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
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.SEARCH_LABELS_ENDPOINT}"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        parameters: Dict[str, Any] = {
            SEARCH_TERM: search_term,
            LOCALE_TAG: language_code,
            LIMIT: limit,
            NEXT_PAGE_ID_TAG: next_page_id,
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=parameters, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return WacomKnowledgeService.__search_results__(response.json())
            raise handle_error(f"Search on labels {search_term} failed. ", response)

    def search_literal(
        self,
        search_term: str,
        literal: OntologyPropertyReference,
        pattern: SearchPattern = SearchPattern.REGEX,
        language_code: LocaleCode = EN_US,
        limit: int = 30,
        next_page_id: str = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[List[ThingObject], str]:
        """
         Search for matches in literals.

         Parameters
         ----------
         search_term: str
             Search term.
         literal: OntologyPropertyReference
             Literal used for the search
         pattern: SearchPattern (default:= SearchPattern.REGEX)
             Search pattern. The chosen search pattern must fit the type of the entity.
         language_code: LocaleCode (default:= EN_US)
             ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
         limit: int (default:= 30)
             Size of the page for pagination.
         next_page_id: str (default:=None)
             ID of the next page within pagination.
         auth_key: Optional[str] = None
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
         results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.SEARCH_LITERALS_ENDPOINT}"
        parameters: Dict[str, Any] = {
            VALUE: search_term,
            LITERAL_PARAMETER: literal.iri,
            LANGUAGE_PARAMETER: language_code,
            LIMIT_PARAMETER: limit,
            SEARCH_PATTERN_PARAMETER: pattern.value,
            NEXT_PAGE_ID_TAG: next_page_id,
        }
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=parameters, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return WacomKnowledgeService.__search_results__(response.json())
            raise handle_error(f"Search on literals {search_term} failed. ", response)

    def search_relation(
        self,
        relation: OntologyPropertyReference,
        language_code: LocaleCode,
        subject_uri: str = None,
        object_uri: str = None,
        limit: int = 30,
        next_page_id: str = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[List[ThingObject], str]:
        """
         Search for matches in literals.

         Parameters
         ----------
         relation: OntologyPropertyReference
             Search term.
         language_code: LocaleCode
             ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
         subject_uri: str (default:=None)
             URI of the subject
         object_uri: str (default:=None)
             URI of the object
         limit: int (default:= 30)
             Size of the page for pagination.
         next_page_id: str (default:=None)
             ID of the next page within pagination.
         auth_key: Optional[str] = None
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
         results: List[ThingObject]
            List of things matching the search term
         next_page_id: str
            ID of the next page.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.SEARCH_RELATION_ENDPOINT}"
        parameters: Dict[str, Any] = {
            SUBJECT_URI: subject_uri,
            RELATION_URI: relation.iri,
            OBJECT_URI: object_uri,
            LANGUAGE_PARAMETER: language_code,
            LIMIT: limit,
            NEXT_PAGE_ID_TAG: next_page_id,
        }
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=parameters, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return WacomKnowledgeService.__search_results__(response.json())
            raise handle_error(
                f"Search on: subject:={subject_uri}, relation {relation.iri}, " f"object:= {object_uri} failed. ",
                response,
            )

    def search_description(
        self,
        search_term: str,
        language_code: LocaleCode,
        limit: int = 30,
        next_page_id: str = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Tuple[List[ThingObject], str]:
        """Search for matches in description.

        Parameters
        ----------
        search_term: str
            Search term.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str (default:=None)
            ID of the next page within pagination.
        auth_key: Optional[str] = None
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
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}{WacomKnowledgeService.SEARCH_DESCRIPTION_ENDPOINT}"
        parameters: Dict[str, Any] = {
            SEARCH_TERM: search_term,
            LOCALE_TAG: language_code,
            LIMIT: limit,
            NEXT_PAGE_ID_TAG: next_page_id,
        }
        headers: dict = {AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}", USER_AGENT_HEADER_FLAG: self.user_agent}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, params=parameters, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return WacomKnowledgeService.__search_results__(response.json())
            raise handle_error(f"Search on labels {search_term}@{language_code} failed. ", response)

    @staticmethod
    def __search_results__(response: Dict[str, Any]) -> Tuple[List[ThingObject], str]:
        """
        Convert response to list of ThingObjects and next page id.

        Parameters
        ----------
        response: Dict[str, Any]
            Response from the service.

        Returns
        -------
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        """
        results: List[ThingObject] = []
        for elem in response["result"]:
            results.append(ThingObject.from_dict(elem))
        return results, response[NEXT_PAGE_ID_TAG]

    def set_entity_image_local(
        self,
        entity_uri: str,
        path: Path,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> str:
        """Setting the image of the entity.
        The image is stored locally.

        Parameters
        ----------
        entity_uri: str
           URI of the entity.
        path: Path
           The path of image.
        auth_key: Optional[str] = None
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
        image_id: str
           ID of uploaded image

        Raises
        ------
        WacomServiceException
           If the graph service returns an error code.
        """
        with path.open("rb") as fp:
            image_bytes: bytes = fp.read()
            file_name: str = str(path.absolute())
            _, file_extension = os.path.splitext(file_name.lower())
            mime_type = MIME_TYPE[file_extension]
            return self.set_entity_image(
                entity_uri,
                image_bytes,
                file_name,
                mime_type,
                auth_key=auth_key,
                timeout=timeout,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
            )

    def set_entity_image_url(
        self,
        entity_uri: str,
        image_url: str,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> str:
        """Setting the image of the entity.
        The image for the URL is downloaded and then pushed to the backend.

        Parameters
        ----------
        auth_key: str
            Auth key from user
        entity_uri: str
            URI of the entity.
        image_url: str
            URL of the image.
        file_name: str (default:=None)
            Name of  the file. If None the name is extracted from URL.
        mime_type: str (default:=None)
            Mime type.
        auth_key: Optional[str] = None
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
        image_id: str
            ID of uploaded image

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        mount_point: str = "https://" if image_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            headers: Dict[str, str] = {USER_AGENT_HEADER_FLAG: self.user_agent}
            response: Response = session.get(image_url, headers=headers, timeout=timeout, verify=self.verify_calls)
            if response.ok:
                image_bytes: bytes = response.content
                file_name: str = image_url if file_name is None else file_name
                if mime_type is None:
                    _, file_extension = os.path.splitext(file_name.lower())
                    if file_extension not in MIME_TYPE:
                        raise handle_error(
                            "Creation of entity image failed. " "Mime-type cannot be identified or is not supported.",
                            response,
                        )
                    mime_type = MIME_TYPE[file_extension]

                return self.set_entity_image(
                    entity_uri,
                    image_bytes,
                    file_name,
                    mime_type,
                    auth_key=auth_key,
                    timeout=timeout,
                    max_retries=max_retries,
                    backoff_factor=backoff_factor,
                )
            raise handle_error("Creation of entity image failed.", response)

    def set_entity_image(
        self,
        entity_uri: str,
        image_byte: bytes,
        file_name: str = "icon.jpg",
        mime_type: str = "image/jpeg",
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> str:
        """Setting the image of the entity.
        The image for the URL is downloaded and then pushed to the backend.

        Parameters
        ----------
        entity_uri: str
           URI of the entity.
        image_byte: bytes
           Binary encoded image.
        file_name: str (default:=None)
           Name of  the file. If None the name is extracted from URL.
        mime_type: str (default:=None)
           Mime type.
        auth_key: Optional[str] = None
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
        image_id: str
           ID of uploaded image

        Raises
        ------
        WacomServiceException
           If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}", USER_AGENT_HEADER_FLAG: self.user_agent}
        files: List[Tuple[str, Tuple[str, bytes, str]]] = [("file", (file_name, image_byte, mime_type))]
        url: str = f"{self.service_base_url}{self.ENTITY_IMAGE_ENDPOINT}{urllib.parse.quote(entity_uri)}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.patch(
                url, headers=headers, files=files, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return response.json()["imageId"]
            raise handle_error("Creation of entity image failed.", response)

    def import_entities(
        self,
        entities: List[ThingObject],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> str:
        """Import entities to the graph.

        Parameters
        ----------
        entities: List[ThingObject]
            List of entities to import.
        auth_key: Optional[str] = None
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
        job_id: str
            ID of the job

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        ndjson_lines: List[str] = []
        for obj in entities:
            data_dict = obj.__import_format_dict__()
            ndjson_lines.append(json.dumps(data_dict))  # Convert each dict to a JSON string

        ndjson_content = "\n".join(ndjson_lines)  # Join JSON strings with newline

        # Compress the NDJSON string to a gzip byte array
        compressed_data: bytes = gzip.compress(ndjson_content.encode("utf-8"))
        files: List[Tuple[str, Tuple[str, bytes, str]]] = [
            ("file", ("import.njson.gz", compressed_data, "application/x-gzip"))
        ]
        url: str = f"{self.service_base_url}{self.IMPORT_ENTITIES_ENDPOINT}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, files=files, timeout=timeout, verify=self.verify_calls
            )
            if response.ok:
                return response.json()["jobId"]
            raise handle_error("Import endpoint returns an error.", response)

    def import_entities_from_file(
        self,
        file_path: Path,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> str:
        """Import entities from a file to the graph.

        Parameters
        ----------
        file_path: Path
            Path to the file containing entities in NDJSON format.
        auth_key: Optional[str] = None
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
        job_id: str
            ID of the job

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        FileNotFoundError
            If the file does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        with file_path.open("rb") as file:
            # Compress the NDJSON string to a gzip byte array
            compressed_data: bytes = file.read()
            files: List[Tuple[str, Tuple[str, bytes, str]]] = [
                ("file", ("import.njson.gz", compressed_data, "application/x-gzip"))
            ]
            url: str = f"{self.service_base_url}{self.IMPORT_ENTITIES_ENDPOINT}"
            mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
            with requests.Session() as session:
                retries: Retry = Retry(
                    total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST
                )
                session.mount(mount_point, HTTPAdapter(max_retries=retries))
                response: Response = session.post(
                    url, headers=headers, files=files, timeout=timeout, verify=self.verify_calls
                )
                if response.ok:
                    return response.json()["jobId"]
                raise handle_error("Import endpoint returns an error.", response)

    def job_status(
        self,
        job_id: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> JobStatus:
        """
        Retrieve the status of the job.

        Parameters
        ----------
        job_id: str
            ID of the job
        auth_key: Optional[str] = None
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
        job_status: JobStatus
            Status of the job
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        url: str = f"{self.service_base_url}{self.IMPORT_ENTITIES_ENDPOINT}/{job_id}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(url, headers=headers, timeout=timeout, verify=self.verify_calls)
            if response.ok:
                return JobStatus.from_dict(response.json())
            raise handle_error(f"Retrieving job status for {job_id} failed.", response)

    def import_error_log(
        self,
        job_id: str,
        auth_key: Optional[str] = None,
        next_page_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> ErrorLogResponse:
        """
        Retrieve the error log of the job.

        Parameters
        ----------
        job_id: str
            ID of the job
        next_page_id: Optional[str] = None
            ID of the next page within pagination.
        auth_key: Optional[str] = None
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
        error: ErrorLogResponse
            Error log of the job
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        url: str = f"{self.service_base_url}{self.IMPORT_ERROR_LOG_ENDPOINT}/{job_id}"
        params: Dict[str, str] = {NEXT_PAGE_ID_TAG: next_page_id} if next_page_id else {}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, timeout=timeout, params=params, verify=self.verify_calls
            )
            if response.ok:
                return ErrorLogResponse.from_dict(response.json())
            raise handle_error(f"Retrieving job status for {job_id} failed.", response)

    def import_new_uris(
        self,
        job_id: str,
        auth_key: Optional[str] = None,
        next_page_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> NewEntityUrisResponse:
        """
        Retrieve the new entity uris from the job.

        Parameters
        ----------
        job_id: str
            ID of the job
        next_page_id: Optional[str] = None
            ID of the next page within pagination.
        auth_key: Optional[str] = None
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
        response: NewEntityUrisResponse
            New entity uris of the job.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        url: str = f"{self.service_base_url}{self.IMPORT_ENTITIES_ENDPOINT}/{job_id}/new-entities"
        params: Dict[str, str] = {NEXT_PAGE_ID_TAG: next_page_id} if next_page_id else {}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, timeout=timeout, params=params, verify=self.verify_calls
            )
            if response.ok:
                return NewEntityUrisResponse.from_dict(response.json())
            raise handle_error(f"Retrieving job status for {job_id} failed.", response)

    # ------------------------------------ Admin endpoints -------------------------------------------------------------

    def rebuild_vector_search_index(
        self,
        prune: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Rebuild the vector search index.

        **Remark:**
        Works for users with role 'TenantAdmin'.

        Parameters
        ----------
        prune: bool
            Prune the index before rebuilding.
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries (default: 3)
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        """
        url: str = f"{self.service_base_url}{WacomKnowledgeService.REBUILD_VECTOR_SEARCH_INDEX}"
        params: Dict[str, str] = {PRUNE_PARAM: prune}
        if UserRole.ADMIN.value not in self.current_session.roles:
            raise WacomServiceException('Only users with role "Admin" can rebuild the vector search index.')
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, params=params, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error("Rebuilding vector search index failed.", response)

    def rebuild_nel_index(
        self,
        nel_index: Literal["Western", "Japanese"],
        prune: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Rebuild the named entity linking index.

        **Remark:**
        Works for users with role 'TenantAdmin'

        Parameters
        ----------
        nel_index: Literal['western', 'japanese']
            Named entity linking index to rebuild.
        prune: bool
            Prune the index before rebuilding.
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.
        """
        url: str = f"{self.service_base_url}{WacomKnowledgeService.REBUILD_NEL_INDEX}"
        params: Dict[str, str] = {PRUNE_PARAM: prune, NEL_PARAM: nel_index}
        if auth_key is None:
            auth_key, _ = self.handle_token()
        if UserRole.ADMIN.value not in self.current_session.roles:
            raise WacomServiceException('Only users with role "Admin" can rebuild the vector search index.')
        auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, params=params, headers=headers, timeout=timeout, verify=self.verify_calls
            )
            if not response.ok:
                raise handle_error("Rebuilding vector search index failed.", response)

    def ontology_update(
        self,
        fix: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Update the ontology.

        **Remark:**
        Works for users with role 'TenantAdmin'.

        Parameters
        ----------
        fix: bool [default:=False]
            Fix the ontology if tenant is in inconsistent state.
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.

        Raises
        ------
        WacomServiceException
            If the graph service returns an error code and commit failed.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f'{self.service_base_url}{WacomKnowledgeService.ONTOLOGY_UPDATE_ENDPOINT}{"/fix" if fix else ""}'
        # Header with auth token
        headers: dict = {USER_AGENT_HEADER_FLAG: self.user_agent, AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}"}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.patch(url, headers=headers, timeout=timeout, verify=self.verify_calls)
            if not response.ok:
                raise handle_error("Ontology update fails.", response)
