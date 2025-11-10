"""
SQL execution actions for running queries against database integrations service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for sqlexec service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString


class BaseActionParams(BaseModel):
    """Base class for all action parameter classes.

    Provides common fields that all actions support:
    - name: The action type identifier
    - step_metadata: Optional configuration for the step created from this action
    """

    name: str
    step_metadata: Optional[Any] = None


class ExecuteParams(BaseActionParams):
    """Execute SQL queries against database integrations and return structured results parameters"""

    name: str = "sqlexec.execute"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    dataset_slug: Optional[Union[str, TemplateString]] = None  # dataset_slug parameter
    store_results: Optional[Union[bool, TemplateString]] = (
        None  # store_results parameter
    )
    encryption_key: Optional[Union[str, TemplateString]] = (
        None  # encryption_key parameter
    )


class ExecuteResult(BaseModel):
    """Execute SQL queries against database integrations and return structured results result type

    Result schema for sqlexec.execute action.
    """

    columns: List[str]
    rows: List[List[Any]]
    row_count: float
    error: Optional[str]


def execute(
    query: Optional[Union[str, TemplateString]] = None,
    dataset_slug: Optional[Union[str, TemplateString]] = None,
    store_results: Optional[Union[bool, TemplateString]] = None,
    encryption_key: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> ExecuteParams:
    """Execute SQL queries against database integrations and return structured results

    Args:
        query: query parameter
        dataset_slug: dataset_slug parameter
        store_results: store_results parameter
        encryption_key: encryption_key parameter

    Returns:
        ExecuteParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "dataset_slug": dataset_slug,
        "store_results": store_results,
        "encryption_key": encryption_key,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ExecuteParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
ExecuteParams._result = ExecuteResult
