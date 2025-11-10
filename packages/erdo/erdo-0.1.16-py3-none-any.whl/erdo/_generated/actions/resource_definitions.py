"""
Resource definition actions for managing and searching data resources service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for resource_definitions service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel

from erdo._generated.types import Resource
from erdo.template import TemplateString


class BaseActionParams(BaseModel):
    """Base class for all action parameter classes.

    Provides common fields that all actions support:
    - name: The action type identifier
    - step_metadata: Optional configuration for the step created from this action
    """

    name: str
    step_metadata: Optional[Any] = None


class SearchParams(BaseActionParams):
    """Search for resource definitions using query and key filters parameters"""

    name: str = "resource_definitions.search"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    or_keys: Optional[Any] = None  # or_keys parameter
    and_keys: Optional[Any] = None  # and_keys parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_id: Optional[Union[str, TemplateString]] = (
        None  # integration_id parameter
    )
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter


class ListParams(BaseActionParams):
    """List resource definitions with optional filtering by dataset, integration, or attach type parameters"""

    name: str = "resource_definitions.list"  # Action type for roundtrip compatibility
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_id: Optional[Union[str, TemplateString]] = (
        None  # integration_id parameter
    )
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    attach_type: Optional[Union[str, TemplateString]] = None  # attach_type parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter


class ListByKeysParams(BaseActionParams):
    """List resource definitions filtered by specific keys with optional additional filters parameters"""

    name: str = (
        "resource_definitions.list_by_keys"  # Action type for roundtrip compatibility
    )
    keys: Optional[Any] = None  # keys parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_id: Optional[Union[str, TemplateString]] = (
        None  # integration_id parameter
    )
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    attach_type: Optional[Union[str, TemplateString]] = None  # attach_type parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter


class SearchFromQueriesParams(BaseActionParams):
    """Search resource definitions using multiple queries including integration-specific queries parameters"""

    name: str = (
        "resource_definitions.search_from_queries"  # Action type for roundtrip compatibility
    )
    integration_queries: Optional[Any] = None  # integration_queries parameter
    or_keys: Optional[Any] = None  # or_keys parameter
    and_keys: Optional[Any] = None  # and_keys parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter
    authorizers: Optional[Any] = None  # authorizers parameter


class SearchResult(BaseModel):
    """Search for resource definitions using query and key filters result type

    Result schema for resource_definitions.search action.
    """

    resource_definitions: List[Resource]


class ListResult(BaseModel):
    """List resource definitions with optional filtering by dataset, integration, or attach type result type

    Result schema for resource_definitions.list action.
    """

    resource_definitions: List[Resource]


class ListByKeysResult(BaseModel):
    """List resource definitions filtered by specific keys with optional additional filters result type

    Result schema for resource_definitions.list_by_keys action.
    """

    resource_definitions: List[Resource]


class SearchFromQueriesResult(BaseModel):
    """Search resource definitions using multiple queries including integration-specific queries result type

    Generic result schema for resource_definitions.search_from_queries action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


def search(
    query: Optional[Union[str, TemplateString]] = None,
    or_keys: Optional[Any] = None,
    and_keys: Optional[Any] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    **params: Any,
) -> SearchParams:
    """Search for resource definitions using query and key filters

    Args:
        query: query parameter
        or_keys: or_keys parameter
        and_keys: and_keys parameter
        thread_id: thread_id parameter
        dataset_id: dataset_id parameter
        integration_id: integration_id parameter
        integration_config_id: integration_config_id parameter
        limit: limit parameter

    Returns:
        SearchParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "or_keys": or_keys,
        "and_keys": and_keys,
        "thread_id": thread_id,
        "dataset_id": dataset_id,
        "integration_id": integration_id,
        "integration_config_id": integration_config_id,
        "limit": limit,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = SearchParams(**param_dict)
    return params_obj


def list(
    thread_id: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    attach_type: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    **params: Any,
) -> ListParams:
    """List resource definitions with optional filtering by dataset, integration, or attach type

    Args:
        thread_id: thread_id parameter
        dataset_id: dataset_id parameter
        integration_id: integration_id parameter
        integration_config_id: integration_config_id parameter
        attach_type: attach_type parameter
        limit: limit parameter

    Returns:
        ListParams: Type-safe parameter object
    """
    param_dict = {
        "thread_id": thread_id,
        "dataset_id": dataset_id,
        "integration_id": integration_id,
        "integration_config_id": integration_config_id,
        "attach_type": attach_type,
        "limit": limit,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ListParams(**param_dict)
    return params_obj


def list_by_keys(
    keys: Optional[Any] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    attach_type: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    **params: Any,
) -> ListByKeysParams:
    """List resource definitions filtered by specific keys with optional additional filters

    Args:
        keys: keys parameter
        thread_id: thread_id parameter
        dataset_id: dataset_id parameter
        integration_id: integration_id parameter
        integration_config_id: integration_config_id parameter
        attach_type: attach_type parameter
        limit: limit parameter

    Returns:
        ListByKeysParams: Type-safe parameter object
    """
    param_dict = {
        "keys": keys,
        "thread_id": thread_id,
        "dataset_id": dataset_id,
        "integration_id": integration_id,
        "integration_config_id": integration_config_id,
        "attach_type": attach_type,
        "limit": limit,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ListByKeysParams(**param_dict)
    return params_obj


def search_from_queries(
    integration_queries: Optional[Any] = None,
    or_keys: Optional[Any] = None,
    and_keys: Optional[Any] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    authorizers: Optional[Any] = None,
    **params: Any,
) -> SearchFromQueriesParams:
    """Search resource definitions using multiple queries including integration-specific queries

    Args:
        integration_queries: integration_queries parameter
        or_keys: or_keys parameter
        and_keys: and_keys parameter
        thread_id: thread_id parameter
        limit: limit parameter
        authorizers: authorizers parameter

    Returns:
        SearchFromQueriesParams: Type-safe parameter object
    """
    param_dict = {
        "integration_queries": integration_queries,
        "or_keys": or_keys,
        "and_keys": and_keys,
        "thread_id": thread_id,
        "limit": limit,
        "authorizers": authorizers,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = SearchFromQueriesParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
SearchParams._result = SearchResult
ListParams._result = ListResult
ListByKeysParams._result = ListByKeysResult
SearchFromQueriesParams._result = SearchFromQueriesResult
