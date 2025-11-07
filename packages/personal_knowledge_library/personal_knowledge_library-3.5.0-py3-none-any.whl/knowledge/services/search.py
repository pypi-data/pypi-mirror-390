# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
from typing import Dict, Any, Optional, List, Literal

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from knowledge.base.language import LocaleCode
from knowledge.base.search import DocumentSearchResponse, LabelMatchingResponse, VectorDBDocument
from knowledge.services import (
    DEFAULT_TIMEOUT,
    AUTHORIZATION_HEADER_FLAG,
    APPLICATION_JSON_HEADER,
    CONTENT_TYPE_HEADER_FLAG,
    USER_AGENT_HEADER_FLAG,
    STATUS_FORCE_LIST,
)
from knowledge.services.base import WacomServiceAPIClient, handle_error


class SemanticSearchClient(WacomServiceAPIClient):
    """
    Semantic Search Client
    ======================
    Client for searching semantically similar documents and labels.

    Parameters
    ----------
    service_url: str
        Service URL for the client.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.
    """

    def __init__(self, service_url: str, service_endpoint: str = "vector/api/v1"):
        super().__init__("Async Semantic Search ", service_url, service_endpoint)

    def retrieve_documents_chunks(
        self,
        locale: LocaleCode,
        uri: str,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
        auth_key: Optional[str] = None,
    ) -> List[VectorDBDocument]:
        """
        Retrieve document chunks from vector database. The service is automatically chunking the document into
        smaller parts. The chunks are returned as a list of dictionaries, with metadata and content.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        uri: str
            URI of the document
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        document: List[VectorDBDocument]:
            List of document chunks with metadata and content related to the document.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}documents/"

        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.get(url, params={"locale": locale, "uri": uri}, headers=headers, timeout=DEFAULT_TIMEOUT)
            if response.ok:
                return [VectorDBDocument(elem) for elem in response.json()]
        raise handle_error(
            "Failed to retrieve the document.", response, headers=headers, parameters={"locale": locale, "uri": uri}
        )

    def retrieve_labels(
        self,
        locale: LocaleCode,
        uri: str,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
        auth_key: Optional[str] = None,
    ) -> List[VectorDBDocument]:
        """
        Retrieve labels from vector database.

        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        document: List[VectorDBDocument]
            List of labels with metadata and content related to the entity with uri.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}labels/"

        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            session.mount(
                mount_point,
                HTTPAdapter(
                    max_retries=Retry(
                        total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST
                    )
                ),
            )
            response = session.get(url, params={"uri": uri, "locale": locale}, headers=headers, timeout=DEFAULT_TIMEOUT)
            if response.ok:
                return [VectorDBDocument(elem) for elem in response.json()]
        raise handle_error(
            "Failed to retrieve the labels.", response, headers=headers, parameters={"locale": locale, "uri": uri}
        )

    def count_documents(
        self,
        locale: LocaleCode,
        concept_type: Optional[str] = None,
        auth_key: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
    ) -> int:
        """
        Count all documents for a tenant.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}documents/count/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {"locale": locale}
        if concept_type:
            params["concept_type"] = concept_type
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.get(url, params=params, headers=headers)
            if response.ok:
                return response.json().get("count", 0)
        raise handle_error("Counting documents failed.", response, headers=headers, parameters={"locale": locale})

    def count_documents_filter(
        self,
        locale: LocaleCode,
        filters: Dict[str, Any],
        auth_key: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
    ) -> int:
        """
        Count all documents for a tenant with filters.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}documents/count/filter/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.post(url, json={"locale": locale, "filter": filters}, headers=headers)
            if response.ok:
                return response.json().get("count", 0)
        raise handle_error(
            "Counting documents failed.", response, headers=headers, parameters={"locale": locale, "filter": filters}
        )

    def count_labels(
        self,
        locale: LocaleCode,
        concept_type: Optional[str] = None,
        auth_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
    ) -> int:
        """
        Count all labels entries for a tenant.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        concept_type: Optional[str] (Default:= None)
            Concept type.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If auth key is provided, it will be used for the request.
        Returns
        -------
        count: int
            Number of words.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}labels/count/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {"locale": locale}
        if concept_type:
            params["concept_type"] = concept_type
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.get(url, params=params, headers=headers, timeout=timeout)
            if response.ok:
                return response.json().get("count", 0)
            raise handle_error("Counting labels failed.", response, headers=headers, parameters={"locale": locale})

    def count_labels_filter(
        self,
        locale: LocaleCode,
        filters: Dict[str, Any],
        auth_key: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
    ) -> int:
        """
        Count all labels for a tenant with filters.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.

        Returns
        -------
        number_of_docs: int
            Number of labels.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}labels/count/filter/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.post(url, json={"locale": locale, "filter": filters}, headers=headers)
            if response.ok:
                return response.json().get("count", 0)
            raise handle_error(
                "Counting labels failed.", response, headers=headers, parameters={"locale": locale, "filter": filters}
            )

    def document_search(
        self,
        query: str,
        locale: LocaleCode,
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 10,
        filter_mode: Optional[Literal["AND", "OR"]] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
        auth_key: Optional[str] = None,
    ) -> DocumentSearchResponse:
        """
        Async Semantic search.

        Parameters
        ----------
        query: str
            Query text for the search
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        filter_mode: Optional[Literal["AND", "OR"]] = None
            Filter mode for the search. If None is provided, the default is "AND".
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        search_results: DocumentSearchResponse
            Search results response.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}documents/search/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {
            "query": query,
            "metadata": filters if filters else {},
            "locale": locale,
            "max_results": max_results,
        }
        if filter_mode:
            params["filter_mode"] = filter_mode
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.post(url, headers=headers, json=params)
            if response.ok:
                response_dict: Dict[str, Any] = response.json()
                return DocumentSearchResponse.from_dict(response_dict)
            raise handle_error("Semantic Search failed.", response, headers=headers, parameters=params)

    def labels_search(
        self,
        query: str,
        locale: LocaleCode,
        filters: Optional[Dict[str, Any]] = None,
        filter_mode: Optional[Literal["AND", "OR"]] = None,
        max_results: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 0.1,
        auth_key: Optional[str] = None,
    ) -> LabelMatchingResponse:
        """
        Async search for semantically similar labels.

        Parameters
        ----------
        query: str
            Query text for the search
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        filter_mode: Optional[Literal["AND", "OR"]] = None
            Filter mode for the search. If None is provided, the default is "AND".
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        list_entities: Dict[str, Any]
            Search results response.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        url: str = f"{self.service_base_url}labels/match/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {
            "query": query,
            "metadata": filters if filters else {},
            "locale": locale,
            "max_results": max_results,
        }
        if filter_mode:
            params["filter_mode"] = filter_mode
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response = session.post(url, headers=headers, json=params)
            if response.ok:
                response_dict: Dict[str, Any] = response.json()
                return LabelMatchingResponse.from_dict(response_dict)
            raise handle_error("Label fuzzy matching failed.", response, headers=headers, parameters=params)
