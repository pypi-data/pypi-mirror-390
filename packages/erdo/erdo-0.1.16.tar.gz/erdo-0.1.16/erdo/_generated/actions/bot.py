"""
Bot service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for Bot service with correct parameter names.
Actual execution happens in the Go backend after syncing.

NOTE: This module is hardcoded because bot.invoke requires bot_name parameter
but the Go struct uses bot_id. The backend converts bot_name -> bot_id internally.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata


class InvokeResult(BaseModel):
    """Bot invoke result type

    Result schema for bot.invoke action.
    """

    result: Any  # The bot invocation result
    messages: list  # Messages from the bot invocation
    resources: list  # Resources created/used during invocation
    final_state: Any  # Final state after invocation


class AskResult(BaseModel):
    """Bot ask result type

    Result schema for bot.ask action.
    """

    success: bool  # Whether the question was successfully processed
    response: Optional[str] = None  # The bot's response to the question
    bot_id: Optional[str] = None  # ID of the bot that answered
    invocation_id: Optional[str] = None  # ID of the invocation
    error: Optional[str] = None  # Error message if ask failed


class BaseActionParams(BaseModel):
    """Base class for all action parameter classes.

    Provides common fields that all actions support:
    - name: The action type identifier
    - step_metadata: Optional configuration for the step created from this action
    """

    name: str
    step_metadata: Optional[Any] = None


class InvokeParams(BaseActionParams):
    """Invoke a bot with specified parameters and return the result parameters"""

    name: str = "bot.invoke"  # Action type for roundtrip compatibility
    bot_key: Optional[Union[str, TemplateString]] = (
        None  # bot_key parameter (unique bot identifier like "erdo.security-checker")
    )
    bot_name: Optional[Union[str, TemplateString]] = (
        None  # bot_name parameter (backend expects this, not bot_id)
    )
    parameters: Optional[Union[Dict[str, Any], TemplateString]] = (
        None  # parameters parameter
    )
    bot_output_visibility_behaviour: Optional[Union[str, TemplateString]] = (
        None  # Output visibility behaviour
    )
    transparent: Optional[Union[bool, TemplateString]] = (
        None  # Whether the invocation is transparent
    )
    disable_tools: Optional[Union[bool, TemplateString]] = (
        None  # Whether to disable tools for this invocation
    )


class AskParams(BaseActionParams):
    """Ask a bot a question and get a response parameters"""

    name: str = "bot.ask"  # Action type for roundtrip compatibility
    query: Optional[Union[str, TemplateString]] = None  # query parameter
    bot_name: Optional[Union[str, TemplateString]] = None  # bot_name parameter
    bot_id: Optional[Union[str, TemplateString]] = None  # bot_id parameter
    invocation_id: Optional[Union[str, TemplateString]] = (
        None  # invocation_id parameter
    )


def invoke(
    bot_key: Optional[Union[str, TemplateString]] = None,
    bot_name: Optional[Union[str, TemplateString]] = None,
    parameters: Optional[Union[Dict[str, Any], TemplateString]] = None,
    bot_output_visibility_behaviour: Optional[Union[str, TemplateString]] = None,
    transparent: Optional[Union[bool, TemplateString]] = None,
    disable_tools: Optional[Union[bool, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> InvokeParams:
    """Invoke a bot with specified parameters and return the result

    The bot.invoke action expects bot_key or bot_name as the parameter.
    The backend will look up the bot and convert to bot_id internally.

    Args:
        bot_key: Unique key of the bot to invoke (e.g., "erdo.security-checker")
        bot_name: Name of the bot to invoke (alternative to bot_key)
        parameters: Parameters to pass to the bot
        bot_output_visibility_behaviour: Output visibility behaviour
        transparent: Whether the invocation is transparent
        disable_tools: Whether to disable tools for this invocation

    Returns:
        InvokeParams: Type-safe parameter object
    """
    params_dict = {
        "bot_key": bot_key,
        "bot_name": bot_name,
        "parameters": parameters,
        "bot_output_visibility_behaviour": bot_output_visibility_behaviour,
        "transparent": transparent,
        "disable_tools": disable_tools,
    }

    # Remove None values for optional parameters
    params_dict = {k: v for k, v in params_dict.items() if v is not None}
    params_dict.update(params)

    # Include step_metadata in params_dict since it's a field on BaseActionParams
    if step_metadata is not None:
        params_dict["step_metadata"] = step_metadata

    # Use normal constructor for proper validation
    return InvokeParams(**params_dict)


def ask(
    query: Optional[Union[str, TemplateString]] = None,
    bot_name: Optional[Union[str, TemplateString]] = None,
    bot_id: Optional[Union[str, TemplateString]] = None,
    invocation_id: Optional[Union[str, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> AskParams:
    """Ask a bot a question and get a response

    Args:
        query: Question to ask the bot
        bot_name: Name of the bot to ask
        bot_id: ID of the bot to ask (alternative to bot_name)
        invocation_id: Invocation ID for tracking

    Returns:
        AskParams: Type-safe parameter object
    """
    params_dict = {
        "query": query,
        "bot_name": bot_name,
        "bot_id": bot_id,
        "invocation_id": invocation_id,
    }

    # Remove None values for optional parameters
    params_dict = {k: v for k, v in params_dict.items() if v is not None}
    params_dict.update(params)

    # Include step_metadata in params_dict since it's a field on BaseActionParams
    if step_metadata is not None:
        params_dict["step_metadata"] = step_metadata

    # Use normal constructor for proper validation
    return AskParams(**params_dict)


# Rebuild models to resolve forward references (needed for Python 3.10+)
InvokeParams.model_rebuild()
AskParams.model_rebuild()

# Associate parameter classes with their result types
InvokeParams._result = InvokeResult
AskParams._result = AskResult
