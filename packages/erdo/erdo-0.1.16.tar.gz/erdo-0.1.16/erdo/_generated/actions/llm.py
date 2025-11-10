"""
LLM service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for LLM service with bot-compatible parameters.
Actual execution happens in the Go backend after syncing.

NOTE: This module is hardcoded to provide bot-compatible parameter names
that match the exported bot code format.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from erdo._generated.types import Tool
from erdo.template import TemplateString
from erdo.types import StepMetadata


class MessageResult(BaseModel):
    """LLM message result type

    Result schema for llm.message action.
    """

    content: str  # The generated response content
    tool_calls: Optional[List[Any]] = None  # Tool calls made by the LLM
    usage: Optional[Any] = None  # Token usage information
    finish_reason: Optional[str] = None  # Reason the generation finished


class BaseActionParams(BaseModel):
    """Base class for all action parameter classes.

    Provides common fields that all actions support:
    - name: The action type identifier
    - step_metadata: Optional configuration for the step created from this action
    """

    name: str
    step_metadata: Optional[StepMetadata] = None


class MessageParams(BaseActionParams):
    """LLM message parameters (bot-compatible)"""

    name: str = "llm.message"  # Action type for roundtrip compatibility

    # Bot definition parameters (high-level)
    system_prompt: Optional[Union[str, TemplateString]] = (
        None  # System prompt for the conversation
    )
    message_history: Optional[Union[List[Dict[str, Any]], TemplateString]] = (
        None  # Previous messages in the conversation
    )
    query: Optional[Union[str, TemplateString]] = None  # User query/message
    context: Optional[Union[str, TemplateString]] = None  # Additional context

    # LLM configuration parameters
    model: Optional[Union[str, TemplateString]] = None  # LLM model to use
    tools: Optional[List[Tool]] = None  # Available tools for the LLM
    response_format: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # Response format specification
    )
    max_tokens: Optional[Union[int, TemplateString]] = (
        None  # Maximum tokens in response
    )
    metadata: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # Additional metadata
    )
    disable_tools: Optional[Union[bool, TemplateString]] = (
        None  # Whether to disable tools for this message
    )
    reasoning: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # Reasoning configuration for extended thinking
    )


def message(
    system_prompt: Optional[Union[str, TemplateString]] = None,
    message_history: Optional[Union[List[Dict[str, Any]], TemplateString]] = None,
    query: Optional[Union[str, TemplateString]] = None,
    context: Optional[Union[str, TemplateString]] = None,
    model: Optional[Union[str, TemplateString]] = None,
    tools: Optional[List[Tool]] = None,
    response_format: Optional[Union[Dict[str, Any], TemplateString]] = None,
    max_tokens: Optional[Union[int, TemplateString]] = None,
    metadata: Optional[Union[Dict[str, Any], TemplateString]] = None,
    disable_tools: Optional[Union[bool, TemplateString]] = None,
    reasoning: Optional[Union[Dict[str, Any], TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> MessageParams:
    """Generate LLM message with bot-compatible parameters

    This function accepts the same parameters that bot definitions use,
    making it compatible with exported bot code.

    Args:
        system_prompt: System prompt for the conversation
        message_history: Previous messages in the conversation
        query: User query/message
        context: Additional context
        model: LLM model to use
        tools: Available tools for the LLM
        response_format: Response format specification
        max_tokens: Maximum tokens in response
        metadata: Additional metadata
        disable_tools: Whether to disable tools for this message
        reasoning: Reasoning configuration for extended thinking

    Returns:
        MessageParams: Type-safe parameter object
    """
    params_dict = {
        "system_prompt": system_prompt,
        "message_history": message_history,
        "query": query,
        "context": context,
        "model": model,
        "tools": tools,
        "response_format": response_format,
        "max_tokens": max_tokens,
        "metadata": metadata,
        "disable_tools": disable_tools,
        "reasoning": reasoning,
    }

    # Remove None values for optional parameters
    params_dict = {k: v for k, v in params_dict.items() if v is not None}
    params_dict.update(params)

    # Include step_metadata in params_dict since it's a field on BaseActionParams
    if step_metadata is not None:
        params_dict["step_metadata"] = step_metadata

    # Use normal constructor for proper validation
    return MessageParams(**params_dict)


# Rebuild models to resolve forward references (needed for Python 3.10+)
MessageParams.model_rebuild()

# Associate parameter classes with their result types
MessageParams._result = MessageResult
