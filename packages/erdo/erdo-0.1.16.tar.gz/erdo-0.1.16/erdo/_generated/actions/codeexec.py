"""
Code execution actions for running and processing code in sandboxed environments service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for codeexec service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, Optional, Union

from pydantic import BaseModel, Field

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
    """Execute code in a sandboxed environment and return the results parameters"""

    name: str = "codeexec.execute"  # Action type for roundtrip compatibility
    entrypoint: Optional[Union[str, TemplateString]] = None  # entrypoint parameter
    code_files: Optional[Any] = None  # code_files parameter
    resources: Optional[Union[str, TemplateString]] = None  # resources parameter
    parameters: Optional[Union[str, TemplateString]] = None  # parameters parameter
    encryption_key: Optional[Union[str, TemplateString]] = (
        None  # encryption_key parameter
    )
    timeout_seconds: Optional[Union[int, TemplateString]] = (
        None  # timeout_seconds parameter
    )
    storage_config: Optional[Any] = None  # storage_config parameter


class ParseFileAsBotResourceParams(BaseActionParams):
    """Parse a file from code execution results into a bot resource with dataset and analysis parameters"""

    name: str = (
        "codeexec.parse_file_as_bot_resource"  # Action type for roundtrip compatibility
    )
    file: Optional[Any] = None  # file parameter
    files_analysis: Optional[Any] = None  # files_analysis parameter
    files_metadata: Optional[Any] = None  # files_metadata parameter
    encryption_key: Optional[Union[str, TemplateString]] = (
        None  # encryption_key parameter
    )


class ParseFileAsJsonParams(BaseActionParams):
    """Parse a file from code execution results as JSON data parameters"""

    name: str = "codeexec.parse_file_as_json"  # Action type for roundtrip compatibility
    file: Optional[Any] = None  # file parameter
    thread_id: Optional[Any] = None  # thread_id parameter


class ExecuteResult(BaseModel):
    """Execute code in a sandboxed environment and return the results result type

    Result schema for codeexec.execute action.
    """

    output: str
    error: Optional[str]
    exit_code: Optional[float]
    files: Optional[Any]


class ParseFileAsBotResourceResult(BaseModel):
    """Parse a file from code execution results into a bot resource with dataset and analysis result type

    Generic result schema for codeexec.parse_file_as_bot_resource action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class ParseFileAsJsonResult(BaseModel):
    """Parse a file from code execution results as JSON data result type

    Result schema for codeexec.parse_file_as_json action.
    """

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    json_data: Any = Field(alias="json")


def execute(
    entrypoint: Optional[Union[str, TemplateString]] = None,
    code_files: Optional[Any] = None,
    resources: Optional[Union[str, TemplateString]] = None,
    parameters: Optional[Union[str, TemplateString]] = None,
    encryption_key: Optional[Union[str, TemplateString]] = None,
    timeout_seconds: Optional[Union[int, TemplateString]] = None,
    storage_config: Optional[Any] = None,
    **params: Any,
) -> ExecuteParams:
    """Execute code in a sandboxed environment and return the results

    Args:
        entrypoint: entrypoint parameter
        code_files: code_files parameter
        resources: resources parameter
        parameters: parameters parameter
        encryption_key: encryption_key parameter
        timeout_seconds: timeout_seconds parameter
        storage_config: storage_config parameter

    Returns:
        ExecuteParams: Type-safe parameter object
    """
    param_dict = {
        "entrypoint": entrypoint,
        "code_files": code_files,
        "resources": resources,
        "parameters": parameters,
        "encryption_key": encryption_key,
        "timeout_seconds": timeout_seconds,
        "storage_config": storage_config,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ExecuteParams(**param_dict)
    return params_obj


def parse_file_as_bot_resource(
    file: Optional[Any] = None,
    files_analysis: Optional[Any] = None,
    files_metadata: Optional[Any] = None,
    encryption_key: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> ParseFileAsBotResourceParams:
    """Parse a file from code execution results into a bot resource with dataset and analysis

    Args:
        file: file parameter
        files_analysis: files_analysis parameter
        files_metadata: files_metadata parameter
        encryption_key: encryption_key parameter

    Returns:
        ParseFileAsBotResourceParams: Type-safe parameter object
    """
    param_dict = {
        "file": file,
        "files_analysis": files_analysis,
        "files_metadata": files_metadata,
        "encryption_key": encryption_key,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ParseFileAsBotResourceParams(**param_dict)
    return params_obj


def parse_file_as_json(
    file: Optional[Any] = None, thread_id: Optional[Any] = None, **params: Any
) -> ParseFileAsJsonParams:
    """Parse a file from code execution results as JSON data

    Args:
        file: file parameter
        thread_id: thread_id parameter

    Returns:
        ParseFileAsJsonParams: Type-safe parameter object
    """
    param_dict = {
        "file": file,
        "thread_id": thread_id,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ParseFileAsJsonParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
ExecuteParams._result = ExecuteResult
ParseFileAsBotResourceParams._result = ParseFileAsBotResourceResult
ParseFileAsJsonParams._result = ParseFileAsJsonResult
