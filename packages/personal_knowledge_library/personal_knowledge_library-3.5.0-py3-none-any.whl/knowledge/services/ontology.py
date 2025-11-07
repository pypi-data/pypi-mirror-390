# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import urllib.parse
from http import HTTPStatus
from typing import Any, Optional, Dict, Tuple, List

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from knowledge.base.entity import FORCE_TAG
from knowledge.base.ontology import (
    OntologyClassReference,
    OntologyPropertyReference,
    OntologyProperty,
    OntologyClass,
    PropertyType,
    THING_CLASS,
    DataPropertyType,
    InflectionSetting,
    Comment,
    OntologyContext,
    OntologyLabel,
    RESOURCE,
)
from knowledge.services import USER_AGENT_HEADER_FLAG, DEFAULT_MAX_RETRIES, DEFAULT_BACKOFF_FACTOR, STATUS_FORCE_LIST
from knowledge.services.base import WacomServiceAPIClient, handle_error
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG

# ------------------------------------------------- Constants ----------------------------------------------------------
BASE_URI_TAG: str = "baseUri"
COMMENTS_TAG: str = "comments"
USER_AGENT_TAG: str = "User-Agent"
DOMAIN_TAG: str = "domains"
ICON_TAG: str = "icon"
INVERSE_OF_TAG: str = "inverseOf"
KIND_TAG: str = "kind"
LABELS_TAG: str = "labels"
LANGUAGE_CODE: str = "lang"
NAME_TAG: str = "name"
CONTEXT_TAG: str = "context"
RANGE_TAG: str = "ranges"
SUB_CLASS_OF_TAG: str = "subClassOf"
SUB_PROPERTY_OF_TAG: str = "subPropertyOf"
LISTING_MODE_PARAM: str = "listingMode"
TEXT_TAG: str = "value"
DEFAULT_TIMEOUT: int = 30


class OntologyService(WacomServiceAPIClient):
    """
    Ontology API Client
    -------------------
    Client to access the ontology service. Offers the following functionality:
    - Listing class names and property names
    - Create new ontology types
    - Update ontology types

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    CONTEXT_ENDPOINT: str = "context"
    CONCEPTS_ENDPOINT: str = "concepts"
    PROPERTIES_ENDPOINT: str = "properties"
    RDF_ENDPOINT: str = "context/{}/versions/rdf"
    PROPERTY_ENDPOINT: str = "context/{}/properties/{}"

    def __init__(self, service_url: str = WacomServiceAPIClient.SERVICE_URL, service_endpoint: str = "ontology/v1"):
        super().__init__(
            application_name="Ontology Service", service_url=service_url, service_endpoint=service_endpoint
        )

    def context(
        self,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Optional[OntologyContext]:
        """
        Getting the information on the context.

        Parameters
        ----------
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
        context_description: Optional[OntologyContext]
            Context of the Ontology
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: dict = {AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}", USER_AGENT_HEADER_FLAG: self.user_agent}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}",
                headers=headers,
                timeout=timeout,
                verify=self.verify_calls,
            )
            if response.ok:
                return OntologyContext.from_dict(response.json())
            return None

    def context_metadata(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[InflectionSetting]:
        """
        Getting the meta-data on the context.

        Parameters
        ----------
        context: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
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
        list_inflection_settings: List[InflectionSetting]
            List of inflection settings.
        """
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
            response: Response = session.get(
                f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}" "/metadata",
                headers=headers,
                timeout=timeout,
                verify=self.verify_calls,
            )
            if response.ok:
                return [
                    InflectionSetting.from_dict(c)
                    for c in response.json()
                    if c.get("concept") is not None and not c.get("concept").startswith("http")
                ]
            raise handle_error("Failed to retrieve context metadata", response, headers=headers)

    def concepts(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[Tuple[OntologyClassReference, OntologyClassReference]]:
        """Retrieve all concept classes.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of the ontology
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
        concepts: List[Tuple[OntologyClassReference, OntologyClassReference]]
            List of ontology classes. Tuple<Classname, Superclass>
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if response.ok:
                response_list: List[Tuple[OntologyClassReference, OntologyClassReference]] = []
                result = response.json()
                for struct in result:
                    response_list.append(
                        (
                            OntologyClassReference.parse(struct[NAME_TAG]),
                            (
                                None
                                if struct[SUB_CLASS_OF_TAG] is None
                                else OntologyClassReference.parse(struct[SUB_CLASS_OF_TAG])
                            ),
                        )
                    )
                return response_list
            raise handle_error("Failed to retrieve concepts", response, headers=headers)

    def concepts_types(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[OntologyClass]:
        """Retrieve all concept class types.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of the ontology
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
        concepts: List[OntologyClass]
            List of ontology classes.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, verify=self.verify_calls, params={LISTING_MODE_PARAM: "Full"}, timeout=timeout
            )
            if response.ok:
                response_list: List[OntologyClass] = []
                for struct in response.json():
                    if struct[NAME_TAG] != RESOURCE:
                        response_list.append(OntologyClass.from_dict(struct))
                return response_list
            raise handle_error("Failed to retrieve concepts", response, headers=headers)

    def properties(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[Tuple[OntologyPropertyReference, OntologyPropertyReference]]:
        """List all properties.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
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
        contexts: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]]
            List of ontology contexts
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/"
                f"{context_url}/{OntologyService.PROPERTIES_ENDPOINT}",
                headers=headers,
                timeout=timeout,
                verify=self.verify_calls,
            )
            # Return empty list if the NOT_FOUND is reported
            if response.status_code == HTTPStatus.NOT_FOUND:
                return []
            if response.ok:
                response_list: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]] = []
                for c in response.json():
                    response_list.append(
                        (
                            OntologyPropertyReference.parse(c[NAME_TAG]),
                            (
                                None
                                if c[SUB_PROPERTY_OF_TAG] is None or c.get(SUB_PROPERTY_OF_TAG) == ""
                                else OntologyPropertyReference.parse(c[SUB_PROPERTY_OF_TAG])
                            ),
                        )
                    )
                return response_list
            raise handle_error("Failed to retrieve properties", response, headers=headers)

    def properties_types(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> List[OntologyProperty]:
        """List all properties types.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
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
        contexts: List[OntologyProperty]
            List of ontology contexts
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/"
                f"{context_url}/{OntologyService.PROPERTIES_ENDPOINT}",
                params={LISTING_MODE_PARAM: "Full"},
                headers=headers,
                timeout=timeout,
                verify=self.verify_calls,
            )
            # Return empty list if the NOT_FOUND is reported
            if response.status_code == HTTPStatus.NOT_FOUND:
                return []
            if response.ok:
                response_list: List[OntologyProperty] = []
                for c in response.json():
                    response_list.append((OntologyProperty.from_dict(c)))
                return response_list
            raise handle_error("Failed to retrieve properties", response, headers=headers)

    def concept(
        self,
        context: str,
        concept_name: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> OntologyClass:
        """Retrieve a concept instance.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        concept_name: str
            IRI of the concept
        auth_key: Optional[str] [default:= None]
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
        instance: OntologyClass
            Instance of the concept
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(concept_name)
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}"
                f"/{OntologyService.CONCEPTS_ENDPOINT}/{concept_url}",
                headers=headers,
                verify=self.verify_calls,
                timeout=timeout,
            )
            if response.ok:
                result: Dict[str, Any] = response.json()
                return OntologyClass.from_dict(result)
            raise handle_error("Failed to retrieve concept", response, headers=headers)

    def property(
        self,
        context: str,
        property_name: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> OntologyProperty:
        """Retrieve a property instance.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        property_name: str
            IRI of the property
        auth_key: Optional[str] [default:= None]
            If auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)

        Returns
        -------
        instance: OntologyProperty
            Instance of the property
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(property_name)
        param: str = f"context/{context_url}/properties/{concept_url}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                f"{self.service_base_url}{param}", headers=headers, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                return OntologyProperty.from_dict(response.json())
            raise handle_error("Failed to retrieve property", response, headers=headers)

    def create_concept(
        self,
        context: str,
        reference: OntologyClassReference,
        subclass_of: OntologyClassReference = THING_CLASS,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, str]:
        """Create concept class.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        subclass_of: OntologyClassReference (default:=wacom:core#Thing)
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
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
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        payload: Dict[str, Any] = {
            SUB_CLASS_OF_TAG: subclass_of.iri,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                result_dict: Dict[str, str] = response.json()
                return result_dict
            raise handle_error("Failed to create concept", response, headers=headers, payload=payload)

    def update_concept(
        self,
        context: str,
        name: str,
        subclass_of: Optional[str],
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, str]:
        """Update concept class.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        name: str
            Name of the concept
        subclass_of: Optional[str]
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
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
        response: Dict[str, str]
            Response from service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        payload: Dict[str, Any] = {
            SUB_CLASS_OF_TAG: subclass_of,
            NAME_TAG: name,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.put(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                return response.json()
            raise handle_error("Failed to update concept", response, headers=headers, payload=payload)

    def delete_concept(
        self,
        context: str,
        reference: OntologyClassReference,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Delete concept class.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
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
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = f"{self.service_base_url}context/{context_url}/concepts/{concept_url}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if not response.ok:
                raise handle_error("Failed to delete concept", response, headers=headers)

    def create_object_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        domains_cls: List[OntologyClassReference],
        ranges_cls: List[OntologyClassReference],
        inverse_of: Optional[OntologyPropertyReference] = None,
        subproperty_of: Optional[OntologyPropertyReference] = None,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, str]:
        """Create property.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: List[OntologyClassReference]
            IRI of the domain
        ranges_cls: List[OntologyClassReference]
            IRI of the range
        inverse_of: Optional[OntologyPropertyReference] (default:= None)
            Inverse property
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
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
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        payload: Dict[str, Any] = {
            KIND_TAG: PropertyType.OBJECT_PROPERTY.value,
            DOMAIN_TAG: [d.iri for d in domains_cls],
            RANGE_TAG: [r.iri for r in ranges_cls],
            SUB_PROPERTY_OF_TAG: subproperty_of.iri if subproperty_of is not None else None,
            INVERSE_OF_TAG: inverse_of.iri if inverse_of is not None else None,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}"
        )
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                return response.json()
            raise handle_error("Failed to create object property", response, headers=headers, payload=payload)

    def create_data_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        domains_cls: List[OntologyClassReference],
        ranges_cls: List[DataPropertyType],
        subproperty_of: Optional[OntologyPropertyReference] = None,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, str]:
        """Create data property.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: List[OntologyClassReference]
            IRI of the domain
        ranges_cls: List[DataPropertyType]
            Data property type
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
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
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        payload: Dict[str, Any] = {
            KIND_TAG: PropertyType.DATA_PROPERTY.value,
            DOMAIN_TAG: [d.iri for d in domains_cls],
            RANGE_TAG: [r.value for r in ranges_cls],
            SUB_PROPERTY_OF_TAG: subproperty_of.iri if subproperty_of is not None else None,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}"
        )
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                return response.json()
            raise handle_error("Failed to create data property", response, headers=headers, payload=payload)

    def delete_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Delete property.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the property
        auth_key: Optional[str] [default:= None]
            If auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
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
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        property_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = f"{self.service_base_url}context/{context_url}/properties/{property_url}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if not response.ok:
                raise handle_error("Failed to delete property", response, headers=headers)

    def create_context(
        self,
        name: str,
        context: Optional[str] = None,
        base_uri: Optional[str] = None,
        icon: Optional[str] = None,
        labels: List[OntologyLabel] = None,
        comments: List[Comment] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> Dict[str, str]:
        """Create context.

        **Remark:**
        Only works for users with role 'TenantAdmin'.

        Parameters
        ----------
        base_uri: str
            Base URI
        name: str
            Name of the context.
        context: Optional[str] [default:= None]
            Context of ontology
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
                timeout: int
            Timeout for the request (default: 60 seconds)
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)

        Returns
        -------
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        if base_uri is None:
            base_uri = f"wacom:{name}#"
        if not base_uri.endswith("#"):
            base_uri += "#"

        payload: Dict[str, Any] = {
            BASE_URI_TAG: base_uri,
            NAME_TAG: name,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        if context is not None:
            payload[CONTEXT_TAG] = context
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.post(
                url, headers=headers, json=payload, verify=self.verify_calls, timeout=timeout
            )
            if response.ok:
                return response.json()
            raise handle_error("Creation of context failed.", response, headers=headers)

    def remove_context(
        self,
        name: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """Remove context.

        Parameters
        ----------
        name: str
            Name of the context
        force: bool (default:= False)
            Force removal of context
        auth_key: Optional[str] [default:= None]
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
        result: Dict[str, str]
            Result from the service
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        url: str = f'{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{name}{"/force" if force else ""}'
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.delete(url, headers=headers, verify=self.verify_calls, timeout=timeout)
            if not response.ok:
                raise handle_error("Removing the context failed.", response, headers=headers)

    def commit(
        self,
        context: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        """
        Commit the ontology.

        Parameters
        ----------
        context: str
            Name of the context.
        force: bool (default:= False)
            Force commit of the ontology.
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}context/{context_url}/commit"
        params: Dict[str, bool] = {FORCE_TAG: force}
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.put(
                url, params=params, headers=headers, verify=self.verify_calls, timeout=timeout
            )
            if not response.ok:
                raise handle_error("Commit of ontology failed.", response, headers=headers)

    def rdf_export(
        self,
        context: str,
        version: int = 0,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ) -> str:
        """
        Export RDF.

        Parameters
        ----------
        context: str
            Name of the context.
        version: int (default:= 0)
            Version of the context if 0 is set the latest version will be exported.
        auth_key: Optional[str] [default:= None]
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
        rdf: str
            Ontology as RDFS / OWL  ontology
        """
        if auth_key is None:
            auth_key, _ = self.handle_token()
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        if version > 0:
            params: Dict[str, int] = {"version": version}
        else:
            params: Dict[str, int] = {}
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}context/{context_url}/versions/rdf"
        mount_point: str = "https://" if self.service_url.startswith("https") else "http://"
        with requests.Session() as session:
            retries: Retry = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=STATUS_FORCE_LIST)
            session.mount(mount_point, HTTPAdapter(max_retries=retries))
            response: Response = session.get(
                url, headers=headers, verify=self.verify_calls, params=params, timeout=timeout
            )
            if response.ok:
                return response.text
            raise handle_error("RDF export failed", response, headers=headers)
