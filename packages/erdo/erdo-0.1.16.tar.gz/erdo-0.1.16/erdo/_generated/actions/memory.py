"""
Memory management actions for storing, searching, and managing memories service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for memory service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field

from erdo._generated.types import Memory
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
    """Search memories using semantic search with optional filters parameters"""

    name: str = "memory.search"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    organization_scope: Optional[Union[str, TemplateString]] = (
        None  # organization_scope parameter
    )
    user_scope: Optional[Union[str, TemplateString]] = None  # user_scope parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    dataset_scope: Optional[Union[str, TemplateString]] = (
        None  # dataset_scope parameter
    )
    integration_config_scope: Optional[Union[str, TemplateString]] = (
        None  # integration_config_scope parameter
    )
    thread_scope: Optional[Union[str, TemplateString]] = None  # thread_scope parameter
    approval_status: Optional[Union[str, TemplateString]] = (
        None  # approval_status parameter
    )
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter
    max_distance: Optional[Any] = None  # max_distance parameter
    authorizers: Optional[Any] = None  # authorizers parameter


class SearchFromQueriesParams(BaseActionParams):
    """Search memories using multiple queries including integration-specific queries parameters"""

    name: str = "memory.search_from_queries"  # Action type for roundtrip compatibility
    queries: Optional[Any] = None  # queries parameter
    integration_queries: Optional[Any] = None  # integration_queries parameter
    organization_scope: Optional[Union[str, TemplateString]] = (
        None  # organization_scope parameter
    )
    user_scope: Optional[Union[str, TemplateString]] = None  # user_scope parameter
    user_id: Optional[Union[str, TemplateString]] = None  # user_id parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    limit: Optional[Union[int, TemplateString]] = None  # limit parameter
    max_distance: Optional[Any] = None  # max_distance parameter
    authorizers: Optional[Any] = None  # authorizers parameter


class StoreParams(BaseActionParams):
    """Store or update a memory with content, metadata, and scope settings parameters"""

    name: str = "memory.store"  # Action type for roundtrip compatibility
    memory: Optional[Any] = None  # memory parameter


class UpdateParams(BaseActionParams):
    """Update an existing memory with new content, metadata, or scope settings parameters"""

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    name: str = "memory.update"  # Action type for roundtrip compatibility
    id_value: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="id"
    )  # id parameter
    content: Optional[Union[str, TemplateString]] = None  # content parameter
    description: Optional[Union[str, TemplateString]] = None  # description parameter
    type_name: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="type"
    )  # type parameter
    searchable_texts: Optional[Any] = None  # searchable_texts parameter
    tags: Optional[Any] = None  # tags parameter
    created_from: Optional[Union[str, TemplateString]] = None  # created_from parameter
    created_by_entity_type: Optional[Union[str, TemplateString]] = (
        None  # created_by_entity_type parameter
    )
    integration_config_id: Optional[Union[str, TemplateString]] = (
        None  # integration_config_id parameter
    )
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    thread_id: Optional[Union[str, TemplateString]] = None  # thread_id parameter
    is_organization_specific: Optional[Union[bool, TemplateString]] = (
        None  # is_organization_specific parameter
    )
    is_user_specific: Optional[Union[bool, TemplateString]] = (
        None  # is_user_specific parameter
    )
    estimated_stale_at: Optional[Union[str, TemplateString]] = (
        None  # estimated_stale_at parameter
    )
    stale_when_text: Optional[Union[str, TemplateString]] = (
        None  # stale_when_text parameter
    )
    extra: Optional[Any] = None  # extra parameter


class DeleteParams(BaseActionParams):
    """Soft delete a memory by marking it as deleted parameters"""

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    name: str = "memory.delete"  # Action type for roundtrip compatibility
    id_value: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="id"
    )  # id parameter


class MarkAsDedupedParams(BaseActionParams):
    """Mark memories as deduplicated by another memory parameters"""

    name: str = "memory.mark_as_deduped"  # Action type for roundtrip compatibility
    memory_ids: Optional[Any] = None  # memory_ids parameter
    deduped_by_id: Optional[Union[str, TemplateString]] = (
        None  # deduped_by_id parameter
    )


class SearchResult(BaseModel):
    """Search memories using semantic search with optional filters result type

    Result schema for memory.search action.
    """

    memories: List[Memory]


class SearchFromQueriesResult(BaseModel):
    """Search memories using multiple queries including integration-specific queries result type

    Generic result schema for memory.search_from_queries action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class StoreResult(BaseModel):
    """Store or update a memory with content, metadata, and scope settings result type

    Result schema for memory.store action.
    """

    memory: Any


class UpdateResult(BaseModel):
    """Update an existing memory with new content, metadata, or scope settings result type

    Generic result schema for memory.update action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class DeleteResult(BaseModel):
    """Soft delete a memory by marking it as deleted result type

    Generic result schema for memory.delete action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class MarkAsDedupedResult(BaseModel):
    """Mark memories as deduplicated by another memory result type

    Generic result schema for memory.mark_as_deduped action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


def search(
    query: Optional[Union[str, TemplateString]] = None,
    organization_scope: Optional[Union[str, TemplateString]] = None,
    user_scope: Optional[Union[str, TemplateString]] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    dataset_scope: Optional[Union[str, TemplateString]] = None,
    integration_config_scope: Optional[Union[str, TemplateString]] = None,
    thread_scope: Optional[Union[str, TemplateString]] = None,
    approval_status: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    max_distance: Optional[Any] = None,
    authorizers: Optional[Any] = None,
    **params: Any,
) -> SearchParams:
    """Search memories using semantic search with optional filters

    Args:
        query: query parameter
        organization_scope: organization_scope parameter
        user_scope: user_scope parameter
        thread_id: thread_id parameter
        dataset_id: dataset_id parameter
        integration_config_id: integration_config_id parameter
        dataset_scope: dataset_scope parameter
        integration_config_scope: integration_config_scope parameter
        thread_scope: thread_scope parameter
        approval_status: approval_status parameter
        limit: limit parameter
        max_distance: max_distance parameter
        authorizers: authorizers parameter

    Returns:
        SearchParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "organization_scope": organization_scope,
        "user_scope": user_scope,
        "thread_id": thread_id,
        "dataset_id": dataset_id,
        "integration_config_id": integration_config_id,
        "dataset_scope": dataset_scope,
        "integration_config_scope": integration_config_scope,
        "thread_scope": thread_scope,
        "approval_status": approval_status,
        "limit": limit,
        "max_distance": max_distance,
        "authorizers": authorizers,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = SearchParams(**param_dict)
    return params_obj


def search_from_queries(
    queries: Optional[Any] = None,
    integration_queries: Optional[Any] = None,
    organization_scope: Optional[Union[str, TemplateString]] = None,
    user_scope: Optional[Union[str, TemplateString]] = None,
    user_id: Optional[Union[str, TemplateString]] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    limit: Optional[Union[int, TemplateString]] = None,
    max_distance: Optional[Any] = None,
    authorizers: Optional[Any] = None,
    **params: Any,
) -> SearchFromQueriesParams:
    """Search memories using multiple queries including integration-specific queries

    Args:
        queries: queries parameter
        integration_queries: integration_queries parameter
        organization_scope: organization_scope parameter
        user_scope: user_scope parameter
        user_id: user_id parameter
        thread_id: thread_id parameter
        limit: limit parameter
        max_distance: max_distance parameter
        authorizers: authorizers parameter

    Returns:
        SearchFromQueriesParams: Type-safe parameter object
    """
    param_dict = {
        "queries": queries,
        "integration_queries": integration_queries,
        "organization_scope": organization_scope,
        "user_scope": user_scope,
        "user_id": user_id,
        "thread_id": thread_id,
        "limit": limit,
        "max_distance": max_distance,
        "authorizers": authorizers,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = SearchFromQueriesParams(**param_dict)
    return params_obj


def store(memory: Optional[Any] = None, **params: Any) -> StoreParams:
    """Store or update a memory with content, metadata, and scope settings

    Args:
        memory: memory parameter

    Returns:
        StoreParams: Type-safe parameter object
    """
    param_dict = {
        "memory": memory,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = StoreParams(**param_dict)
    return params_obj


def update(
    id_value: Optional[Union[str, TemplateString]] = None,
    content: Optional[Union[str, TemplateString]] = None,
    description: Optional[Union[str, TemplateString]] = None,
    type_name: Optional[Union[str, TemplateString]] = None,
    searchable_texts: Optional[Any] = None,
    tags: Optional[Any] = None,
    created_from: Optional[Union[str, TemplateString]] = None,
    created_by_entity_type: Optional[Union[str, TemplateString]] = None,
    integration_config_id: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    thread_id: Optional[Union[str, TemplateString]] = None,
    is_organization_specific: Optional[Union[bool, TemplateString]] = None,
    is_user_specific: Optional[Union[bool, TemplateString]] = None,
    estimated_stale_at: Optional[Union[str, TemplateString]] = None,
    stale_when_text: Optional[Union[str, TemplateString]] = None,
    extra: Optional[Any] = None,
    **params: Any,
) -> UpdateParams:
    """Update an existing memory with new content, metadata, or scope settings

    Args:
        id_value: id parameter
        content: content parameter
        description: description parameter
        type_name: type parameter
        searchable_texts: searchable_texts parameter
        tags: tags parameter
        created_from: created_from parameter
        created_by_entity_type: created_by_entity_type parameter
        integration_config_id: integration_config_id parameter
        dataset_id: dataset_id parameter
        thread_id: thread_id parameter
        is_organization_specific: is_organization_specific parameter
        is_user_specific: is_user_specific parameter
        estimated_stale_at: estimated_stale_at parameter
        stale_when_text: stale_when_text parameter
        extra: extra parameter

    Returns:
        UpdateParams: Type-safe parameter object
    """
    param_dict = {
        "id": id_value,
        "content": content,
        "description": description,
        "type": type_name,
        "searchable_texts": searchable_texts,
        "tags": tags,
        "created_from": created_from,
        "created_by_entity_type": created_by_entity_type,
        "integration_config_id": integration_config_id,
        "dataset_id": dataset_id,
        "thread_id": thread_id,
        "is_organization_specific": is_organization_specific,
        "is_user_specific": is_user_specific,
        "estimated_stale_at": estimated_stale_at,
        "stale_when_text": stale_when_text,
        "extra": extra,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = UpdateParams(**param_dict)
    return params_obj


def delete(
    id_value: Optional[Union[str, TemplateString]] = None, **params: Any
) -> DeleteParams:
    """Soft delete a memory by marking it as deleted

    Args:
        id_value: id parameter

    Returns:
        DeleteParams: Type-safe parameter object
    """
    param_dict = {
        "id": id_value,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = DeleteParams(**param_dict)
    return params_obj


def mark_as_deduped(
    memory_ids: Optional[Any] = None,
    deduped_by_id: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> MarkAsDedupedParams:
    """Mark memories as deduplicated by another memory

    Args:
        memory_ids: memory_ids parameter
        deduped_by_id: deduped_by_id parameter

    Returns:
        MarkAsDedupedParams: Type-safe parameter object
    """
    param_dict = {
        "memory_ids": memory_ids,
        "deduped_by_id": deduped_by_id,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = MarkAsDedupedParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
SearchParams._result = SearchResult
SearchFromQueriesParams._result = SearchFromQueriesResult
StoreParams._result = StoreResult
UpdateParams._result = UpdateResult
DeleteParams._result = DeleteResult
MarkAsDedupedParams._result = MarkAsDedupedResult
