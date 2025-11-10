"""
Basic utility actions for data manipulation and control flow service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for utils service.
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


class EchoParams(BaseActionParams):
    """Echo parameters back as output parameters"""

    name: str = "utils.echo"  # Action type for roundtrip compatibility
    data: Optional[Any] = None  # data parameter


class ParseJsonParams(BaseActionParams):
    """Parse JSON string and validate required keys parameters"""

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    name: str = "utils.parse_json"  # Action type for roundtrip compatibility
    json_data: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="json"
    )  # json parameter
    required_keys: Optional[Any] = None  # required_keys parameter


class ConcatParams(BaseActionParams):
    """Concatenate arrays or strings from specified keys parameters"""

    name: str = "utils.concat"  # Action type for roundtrip compatibility
    concat: Optional[Any] = None  # concat parameter
    data: Optional[Any] = None  # data parameter


class CastParams(BaseActionParams):
    """Cast string values to different types (string, integer, float, bool) parameters"""

    model_config = {"populate_by_name": True}  # Allow both field names and aliases

    name: str = "utils.cast"  # Action type for roundtrip compatibility
    value: Optional[Union[str, TemplateString]] = None  # value parameter
    type_name: Optional[Union[str, TemplateString]] = Field(
        default=None, alias="type"
    )  # type parameter


class RaiseParams(BaseActionParams):
    """Raise a status with message and parameters parameters"""

    name: str = "utils.raise"  # Action type for roundtrip compatibility
    status: Optional[Union[str, TemplateString]] = None  # status parameter
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    parameters: Optional[Any] = None  # parameters parameter


class CaptureExceptionParams(BaseActionParams):
    """Capture an exception to Sentry and return an error result parameters"""

    name: str = "utils.capture_exception"  # Action type for roundtrip compatibility
    exception: Optional[Union[str, TemplateString]] = None  # exception parameter
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    error_type: Optional[Union[str, TemplateString]] = None  # error_type parameter


class SendStatusParams(BaseActionParams):
    """Send a status event to the client parameters"""

    name: str = "utils.send_status"  # Action type for roundtrip compatibility
    status: Optional[Union[str, TemplateString]] = None  # status parameter
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    details: Optional[Any] = None  # details parameter


class WriteParams(BaseActionParams):
    """Write output message with specified content types parameters"""

    name: str = "utils.write"  # Action type for roundtrip compatibility
    message: Optional[Union[str, TemplateString]] = None  # message parameter
    content_type: Optional[Union[str, TemplateString]] = None  # content_type parameter
    history_content_type: Optional[Union[str, TemplateString]] = (
        None  # history_content_type parameter
    )
    ui_content_type: Optional[Union[str, TemplateString]] = (
        None  # ui_content_type parameter
    )
    output_channels: Optional[Any] = None  # output_channels parameter


class ProcessIntegrationQueriesParams(BaseActionParams):
    """Process integration queries to create resource-specific search queries parameters"""

    name: str = (
        "utils.process_integration_queries"  # Action type for roundtrip compatibility
    )
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    resource: Optional[Any] = None  # resource parameter
    queries: Optional[Any] = None  # queries parameter


class EchoResult(BaseModel):
    """Echo parameters back as output result type

    Generic result schema for utils.echo action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class ParseJsonResult(BaseModel):
    """Parse JSON string and validate required keys result type

    Generic result schema for utils.parse_json action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class ConcatResult(BaseModel):
    """Concatenate arrays or strings from specified keys result type

    Generic result schema for utils.concat action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class CastResult(BaseModel):
    """Cast string values to different types (string, integer, float, bool) result type

    Generic result schema for utils.cast action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class RaiseResult(BaseModel):
    """Raise a status with message and parameters result type

    Generic result schema for utils.raise action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class CaptureExceptionResult(BaseModel):
    """Capture an exception to Sentry and return an error result result type

    Generic result schema for utils.capture_exception action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class SendStatusResult(BaseModel):
    """Send a status event to the client result type

    Generic result schema for utils.send_status action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class WriteResult(BaseModel):
    """Write output message with specified content types result type

    Generic result schema for utils.write action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


class ProcessIntegrationQueriesResult(BaseModel):
    """Process integration queries to create resource-specific search queries result type

    Generic result schema for utils.process_integration_queries action.
    """

    success: bool = True  # Whether the action was successful

    class Config:
        extra = "allow"  # Allow additional fields dynamically


def echo(data: Optional[Any] = None, **params: Any) -> EchoParams:
    """Echo parameters back as output

    Args:
        data: data parameter

    Returns:
        EchoParams: Type-safe parameter object
    """
    param_dict = {
        "data": data,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = EchoParams(**param_dict)
    return params_obj


def parse_json(
    json_data: Optional[Union[str, TemplateString]] = None,
    required_keys: Optional[Any] = None,
    **params: Any,
) -> ParseJsonParams:
    """Parse JSON string and validate required keys

    Args:
        json_data: json parameter
        required_keys: required_keys parameter

    Returns:
        ParseJsonParams: Type-safe parameter object
    """
    param_dict = {
        "json": json_data,
        "required_keys": required_keys,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ParseJsonParams(**param_dict)
    return params_obj


def concat(
    concat: Optional[Any] = None, data: Optional[Any] = None, **params: Any
) -> ConcatParams:
    """Concatenate arrays or strings from specified keys

    Args:
        concat: concat parameter
        data: data parameter

    Returns:
        ConcatParams: Type-safe parameter object
    """
    param_dict = {
        "concat": concat,
        "data": data,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ConcatParams(**param_dict)
    return params_obj


def cast(
    value: Optional[Union[str, TemplateString]] = None,
    type_name: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> CastParams:
    """Cast string values to different types (string, integer, float, bool)

    Args:
        value: value parameter
        type_name: type parameter

    Returns:
        CastParams: Type-safe parameter object
    """
    param_dict = {
        "value": value,
        "type": type_name,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = CastParams(**param_dict)
    return params_obj


def raise_error(
    status: Optional[Union[str, TemplateString]] = None,
    message: Optional[Union[str, TemplateString]] = None,
    parameters: Optional[Any] = None,
    **params: Any,
) -> RaiseParams:
    """Raise a status with message and parameters

    Args:
        status: status parameter
        message: message parameter
        parameters: parameters parameter

    Returns:
        RaiseParams: Type-safe parameter object
    """
    param_dict = {
        "status": status,
        "message": message,
        "parameters": parameters,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = RaiseParams(**param_dict)
    return params_obj


def capture_exception(
    exception: Optional[Union[str, TemplateString]] = None,
    message: Optional[Union[str, TemplateString]] = None,
    error_type: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> CaptureExceptionParams:
    """Capture an exception to Sentry and return an error result

    Args:
        exception: exception parameter
        message: message parameter
        error_type: error_type parameter

    Returns:
        CaptureExceptionParams: Type-safe parameter object
    """
    param_dict = {
        "exception": exception,
        "message": message,
        "error_type": error_type,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = CaptureExceptionParams(**param_dict)
    return params_obj


def send_status(
    status: Optional[Union[str, TemplateString]] = None,
    message: Optional[Union[str, TemplateString]] = None,
    details: Optional[Any] = None,
    **params: Any,
) -> SendStatusParams:
    """Send a status event to the client

    Args:
        status: status parameter
        message: message parameter
        details: details parameter

    Returns:
        SendStatusParams: Type-safe parameter object
    """
    param_dict = {
        "status": status,
        "message": message,
        "details": details,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = SendStatusParams(**param_dict)
    return params_obj


def write(
    message: Optional[Union[str, TemplateString]] = None,
    content_type: Optional[Union[str, TemplateString]] = None,
    history_content_type: Optional[Union[str, TemplateString]] = None,
    ui_content_type: Optional[Union[str, TemplateString]] = None,
    output_channels: Optional[Any] = None,
    **params: Any,
) -> WriteParams:
    """Write output message with specified content types

    Args:
        message: message parameter
        content_type: content_type parameter
        history_content_type: history_content_type parameter
        ui_content_type: ui_content_type parameter
        output_channels: output_channels parameter

    Returns:
        WriteParams: Type-safe parameter object
    """
    param_dict = {
        "message": message,
        "content_type": content_type,
        "history_content_type": history_content_type,
        "ui_content_type": ui_content_type,
        "output_channels": output_channels,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = WriteParams(**param_dict)
    return params_obj


def process_integration_queries(
    query: Optional[Union[str, TemplateString]] = None,
    resource: Optional[Any] = None,
    queries: Optional[Any] = None,
    **params: Any,
) -> ProcessIntegrationQueriesParams:
    """Process integration queries to create resource-specific search queries

    Args:
        query: query parameter
        resource: resource parameter
        queries: queries parameter

    Returns:
        ProcessIntegrationQueriesParams: Type-safe parameter object
    """
    param_dict = {
        "query": query,
        "resource": resource,
        "queries": queries,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ProcessIntegrationQueriesParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
EchoParams._result = EchoResult
ParseJsonParams._result = ParseJsonResult
ConcatParams._result = ConcatResult
CastParams._result = CastResult
RaiseParams._result = RaiseResult
CaptureExceptionParams._result = CaptureExceptionResult
SendStatusParams._result = SendStatusResult
WriteParams._result = WriteResult
ProcessIntegrationQueriesParams._result = ProcessIntegrationQueriesResult
