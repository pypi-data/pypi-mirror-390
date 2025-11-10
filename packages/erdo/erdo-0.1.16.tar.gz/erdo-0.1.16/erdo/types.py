"""
Erdo Agent SDK - Core Types

This file contains the main SDK classes for building AI agents.
Auto-generated types are imported from the generated module.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union, cast

from pydantic import BaseModel, Field, field_serializer, model_serializer

from ._generated.types import (
    BotResource,
    Dataset,
    DatasetType,
    ExecutionModeType,
    HandlerType,
    OutputContentType,
    OutputVisibility,
    ParameterDefinition,
    ParameterHydrationBehaviour,
    Tool,
)
from .bot_permissions import (
    BotPermissions,
    check_bot_access,
    get_bot_permissions,
    set_bot_org_permission,
    set_bot_public,
    set_bot_user_permission,
)
from .template import TemplateString

# Type aliases for complex types that are json.RawMessage in Go
ExecutionCondition = Dict[str, Any]  # Complex execution condition configuration


# Protocols for better type safety
class ActionProtocol(Protocol):
    """Protocol for action objects that can be converted to parameters."""

    name: str

    def model_dump(self) -> Dict[str, Any]: ...


class StepLike(Protocol):
    """Protocol for step-like objects."""

    key: Optional[str]
    id: Optional[str]


class ConditionProtocol(Protocol):
    """Protocol for condition objects."""

    def to_dict(self) -> Dict[str, Any]: ...


class ExecutionModeProtocol(Protocol):
    """Protocol for execution mode objects."""

    def to_dict(self) -> Dict[str, Any]: ...


class PythonFile(BaseModel):
    """Reference to a Python file for code execution.

    Can be used in code_files parameter to reference local Python files.
    When used, the file content will be automatically loaded during export.
    """

    filename: str = Field(
        ..., description="Path to the file (e.g., 'analyze_file_files/analyze.py')"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format for serialization."""
        return {
            "filename": self.filename,
            "_type": "PythonFile",  # Marker to identify this as a file reference
        }

    @model_serializer
    def _serialize_model(self) -> Dict[str, Any]:
        """Pydantic v2 serializer - always use our custom format."""
        return self.to_dict()

    def resolve_content(self, base_path: Optional[str] = None) -> Dict[str, str]:
        """Resolve the file content for inclusion in code_files.

        Args:
            base_path: Base directory path to resolve relative paths

        Returns:
            Dict with filename and content
        """
        if base_path is None:
            base_path = os.getcwd()

        file_path = Path(base_path) / self.filename

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Return just the base filename, not the full path
            base_filename = Path(self.filename).name
            return {"filename": base_filename, "content": content}
        except FileNotFoundError:
            raise FileNotFoundError(f"Python file not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading Python file {file_path}: {e}")


def _extract_step_config_from_action(action: Any) -> Dict[str, Any]:
    """Extract step configuration from an action object.

    Actions can include a step_metadata parameter that configures the Step properties.
    This function extracts those properties and returns them as a dict for Step(**config).

    Example:
        utils.echo(
            data={"result": "value"},
            step_metadata=StepMetadata(
                key="my_step",
                output_behavior={"result": OutputBehaviorType.MERGE}
            )
        )

    The step_metadata fields are extracted and used to configure the Step:
    - key: Step identifier
    - output_behavior: How output fields are merged into state
    - execution_mode: Parallel/sequential/background/iterate
    - depends_on: Step dependencies
    - output_channels: Where output is sent
    - visibility settings: User and bot visibility
    - messages: Running/finished messages
    - content types: Output/history/UI content types

    Args:
        action: Action object (from utils.echo, llm.message, etc.)

    Returns:
        Dict with 'action' and any extracted step_metadata fields
    """
    step_config: Dict[str, Any] = {"action": action}

    # Extract step_metadata if present on the action object
    if hasattr(action, "step_metadata") and action.step_metadata is not None:
        metadata = action.step_metadata

        # Extract each metadata field if it's set (not None)
        if hasattr(metadata, "key") and metadata.key:
            step_config["key"] = metadata.key
        if hasattr(metadata, "depends_on") and metadata.depends_on:
            step_config["depends_on"] = metadata.depends_on
        if hasattr(metadata, "execution_mode") and metadata.execution_mode:
            step_config["execution_mode"] = metadata.execution_mode
        if hasattr(metadata, "output_behavior") and metadata.output_behavior:
            step_config["output_behavior"] = metadata.output_behavior
        if hasattr(metadata, "output_channels") and metadata.output_channels:
            step_config["output_channels"] = metadata.output_channels
        if hasattr(metadata, "output_content_type") and metadata.output_content_type:
            step_config["output_content_type"] = metadata.output_content_type
        if hasattr(metadata, "history_content_type") and metadata.history_content_type:
            step_config["history_content_type"] = metadata.history_content_type
        if hasattr(metadata, "ui_content_type") and metadata.ui_content_type:
            step_config["ui_content_type"] = metadata.ui_content_type
        if (
            hasattr(metadata, "user_output_visibility")
            and metadata.user_output_visibility
        ):
            step_config["user_output_visibility"] = metadata.user_output_visibility
        if (
            hasattr(metadata, "bot_output_visibility")
            and metadata.bot_output_visibility
        ):
            step_config["bot_output_visibility"] = metadata.bot_output_visibility
        if hasattr(metadata, "running_message") and metadata.running_message:
            step_config["running_message"] = metadata.running_message
        if hasattr(metadata, "finished_message") and metadata.finished_message:
            step_config["finished_message"] = metadata.finished_message
        if (
            hasattr(metadata, "parameter_hydration_behaviour")
            and metadata.parameter_hydration_behaviour
        ):
            step_config["parameter_hydration_behaviour"] = (
                metadata.parameter_hydration_behaviour
            )

    return step_config


class StepMetadata(BaseModel):
    """Metadata for workflow steps, containing configuration and execution parameters.

    StepMetadata is used to configure step properties when creating steps via actions.
    It's particularly useful in result handlers where you need to configure step behavior:

    Example:
        step.on(IsSuccess(),
            utils.parse_json(
                json_data="{{output}}",
                step_metadata=StepMetadata(
                    key="parse_result",
                    output_behavior={"data": OutputBehaviorType.MERGE}
                )
            )
        )

    Fields:
        key: Step identifier (used for referencing in templates and dependencies)
        output_behavior: Controls how output fields are merged into state
            - STEP_ONLY: Output only available via steps.step_key.field
            - MERGE: Output fields merged into root state
            - OVERWRITE: Output replaces entire state
        execution_mode: How the step executes (sequential/parallel/background/iterate)
        depends_on: Other steps this step depends on
        output_channels: Where step output is sent (e.g., ["user", "bot"])
        visibility: Control who sees the output (user/bot)
        messages: Custom running/finished messages
        content_types: Specify output/history/UI content types
    """

    model_config = {"arbitrary_types_allowed": True}

    key: Optional[str] = None
    depends_on: Union[List[Union[Any, str]], None] = (
        None  # Can be Step objects or strings
    )
    execution_mode: Optional[Union[Any, Dict[str, Any]]] = (
        None  # Can be ExecutionMode object or dict
    )
    output_behavior: Optional[Dict[str, Any]] = None
    output_channels: List[str] = Field(default_factory=list)
    output_content_type: OutputContentType = OutputContentType.TEXT
    history_content_type: Optional[str] = None
    ui_content_type: Optional[str] = None
    user_output_visibility: OutputVisibility = OutputVisibility.VISIBLE
    bot_output_visibility: OutputVisibility = OutputVisibility.HIDDEN
    running_message: Optional[Union[str, TemplateString]] = None
    finished_message: Optional[Union[str, TemplateString]] = None
    parameter_hydration_behaviour: Optional[ParameterHydrationBehaviour] = None

    @field_serializer(
        "running_message", "finished_message", mode="wrap", when_used="always"
    )
    def serialize_message_fields(
        self, value: Optional[Union[str, TemplateString]], _info
    ) -> Optional[str]:
        """Convert TemplateString to str during serialization."""
        if isinstance(value, TemplateString):
            return str(value)
        return value


class Step(StepMetadata):
    """A single step in an agent workflow."""

    agent: Optional[Any] = None  # Reference to the agent this step belongs to
    result_handler: Optional[Any] = (
        None  # Reference to the result handler this step belongs to
    )
    action: Union[Any, Dict[str, Any]]  # Function call like codeexec.execute(...)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result_handlers: List["ResultHandler"] = Field(default_factory=list)

    def __init__(self, action: Any = None, step: Optional["Step"] = None, **data: Any):
        # Validate that only one of action or step is provided
        if action is not None and step is not None:
            raise ValueError("Cannot specify both 'action' and 'step' parameters")

        if action is None and step is None:
            raise ValueError("Must specify either 'action' or 'step' parameter")

        if step is not None:
            # Copy all fields from the provided step
            # Type check is redundant due to type annotation, but kept for runtime safety
            if not hasattr(step, "action"):
                raise ValueError("'step' parameter must be a Step object")

            # Copy fields directly to preserve object types (especially action)
            # Don't use model_dump() as it serializes objects to dicts
            data.update(
                {
                    "action": step.action,
                    "key": step.key,
                    "parameters": step.parameters,
                    "depends_on": step.depends_on,
                    "execution_mode": step.execution_mode,
                    "output_behavior": step.output_behavior,
                    "result_handlers": step.result_handlers,
                    "output_channels": step.output_channels,
                    "output_content_type": step.output_content_type,
                    "history_content_type": step.history_content_type,
                    "ui_content_type": step.ui_content_type,
                    "user_output_visibility": step.user_output_visibility,
                    "bot_output_visibility": step.bot_output_visibility,
                    "running_message": step.running_message,
                    "finished_message": step.finished_message,
                    "parameter_hydration_behaviour": step.parameter_hydration_behaviour,
                }
            )
        else:
            # Standard action-based step
            data["action"] = action

            # Handle step_metadata - can be provided as kwarg or on action object
            step_metadata = None
            if "step_metadata" in data and data["step_metadata"] is not None:
                step_metadata = data.pop("step_metadata")
            elif (
                hasattr(action, "step_metadata")
                and getattr(action, "step_metadata", None) is not None
            ):
                step_metadata = getattr(action, "step_metadata")

            if step_metadata is not None:
                # Extract all fields from StepMetadata
                if hasattr(step_metadata, "model_dump"):
                    metadata_dict = step_metadata.model_dump(exclude_none=True)
                    # Apply metadata fields, but don't overwrite explicitly provided fields
                    for key, value in metadata_dict.items():
                        if key not in data:
                            data[key] = value
                elif isinstance(step_metadata, dict):
                    # If it's already a dict, apply it
                    for key, value in step_metadata.items():
                        if key not in data and value is not None:
                            data[key] = value

        super().__init__(**data)
        # For enhanced syntax support - use private field not tracked by pydantic
        self._decorator_handlers: List[Tuple[Any, Callable[..., Any]]] = []

        # Automatically register with agent if provided and this is not a nested step
        if self.agent is not None and self.result_handler is None:
            self.agent.add_step(self)

    def extract_action_parameters(self) -> Dict[str, Any]:
        """Extract parameters from the action object safely."""
        if not self.action:
            return {}

        # Handle nested Step objects (for result handlers)
        if isinstance(self.action, Step):
            return self.action.extract_action_parameters()

        # If action is a Pydantic model, get its dict representation
        if hasattr(self.action, "model_dump") and callable(
            getattr(self.action, "model_dump")
        ):
            try:
                action_obj = cast(ActionProtocol, self.action)
                params = action_obj.model_dump()
                # Remove the redundant 'name' field since it's already known from action type
                params.pop("name", None)
                # Remove step_metadata - it's for Step config, not action parameters
                params.pop("step_metadata", None)
                # Map Python SDK field names to backend field names
                if "json_data" in params:
                    params["json"] = params.pop("json_data")
                # Remove None values for optional parameters (matches action function behavior)
                params = {k: v for k, v in params.items() if v is not None}
                # Sort parameters for deterministic output
                return dict(sorted(params.items()))
            except Exception:
                return {}
        elif hasattr(self.action, "dict") and callable(getattr(self.action, "dict")):
            try:
                # Legacy pydantic v1 support
                action_dict_method = getattr(self.action, "dict")
                params = action_dict_method()
                # Remove the redundant 'name' field since it's already known from action type
                params.pop("name", None)
                # Remove step_metadata - it's for Step config, not action parameters
                params.pop("step_metadata", None)
                # Map Python SDK field names to backend field names
                if "json_data" in params:
                    params["json"] = params.pop("json_data")
                # Remove None values for optional parameters (matches action function behavior)
                params = {k: v for k, v in params.items() if v is not None}
                # Sort parameters for deterministic output
                return dict(sorted(params.items()))
            except Exception:
                return {}
        elif isinstance(self.action, dict):
            # Map Python SDK field names to backend field names
            dict_params: Dict[str, Any] = dict(self.action)
            # Remove the redundant 'name' field since it's already known from action type
            dict_params.pop("name", None)
            if "json_data" in dict_params:
                dict_params["json"] = dict_params.pop("json_data")
            # Sort parameters for deterministic output
            return dict(sorted(dict_params.items()))
        else:
            return {}

    def get_action_type(self) -> str:
        """Get the action type string safely."""
        if not self.action:
            raise ValueError("Action is not set")

        # Handle nested Step objects (for result handlers)
        if isinstance(self.action, Step):
            return self.action.get_action_type()

        # Action objects should have a name attribute with the action type
        if hasattr(self.action, "name"):
            name_attr = getattr(self.action, "name")
            if isinstance(name_attr, str):
                return name_attr
            elif hasattr(name_attr, "__str__"):
                return str(name_attr)

        # Fallback for unexpected cases
        return str(type(self.action).__name__).lower()

    def get_depends_on_keys(self) -> Optional[List[str]]:
        """Get dependency keys safely without circular references,
        preserving None vs [] distinction."""
        # CRITICAL: Preserve None vs [] distinction for 100% roundtrip parity
        if self.depends_on is None:
            return None  # Explicitly return None for null dependencies

        if not self.depends_on:  # Empty list case
            return []

        # Depends_on is guaranteed to be a non-empty list at this point
        depends_list = self.depends_on

        result: List[str] = []
        for dep in depends_list:
            if isinstance(dep, str):
                # Already a string identifier
                result.append(dep)
            elif hasattr(dep, "key") and getattr(dep, "key", None):
                # Prefer the step key if available
                key_val = getattr(dep, "key")
                result.append(str(key_val) if key_val is not None else "")
            elif hasattr(dep, "id") and getattr(dep, "id", None):
                # Fall back to step ID if no key
                id_val = getattr(dep, "id")
                result.append(str(id_val) if id_val is not None else "")
            else:
                # Fail if we can't get a valid identifier
                raise ValueError(f"Step dependency has no key or id: {dep}")
        return result

    @property
    def output(self) -> "StepOutput":
        """Get typed output reference for this step."""
        return StepOutput(step_key=self.key or f"step_{id(self)}")

    def when(
        self, condition: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator for adding result handlers with conditions.

        Usage:
        @step.when(IsSuccess() & GreaterThan("confidence", 0.8))
        def handle_high_confidence(result):
            return store_analysis(result)
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Store the handler function and condition for later processing
            self._decorator_handlers.append((condition, func))
            return func

        return decorator

    def on(
        self,
        condition: Any,
        *actions: Any,
        handler_type: HandlerType = HandlerType.INTERMEDIATE,
    ) -> "Step":
        """Add a result handler with condition and action(s).

        Usage:
        # Single action
        step.on(IsSuccess(), utils.store_analysis(data=state.analyze_step.output))

        # Multiple actions (variadic arguments)
        step.on(And(IsError(), LessThan(number='r"{{coalesce "code_retry_loops?" 0}}"', value="2")),
            send_status(status="retrying", message="Code execution failed, attempting to fix..."),
            utils.echo(data={"code_retry_loops": 'r"{{incrementCounter "code_retry_loops"}}'}),
            raise_action(status="go to step", message="code", parameters={...})
        )
        """
        if not actions:
            raise ValueError("Must specify at least one action")

        # Create steps for each action, handling Step objects correctly
        step_actions: List[Step] = []
        for action in actions:
            if isinstance(action, Step):
                # If it's already a Step, use step= parameter
                step_actions.append(Step(step=action))
            else:
                # Extract step_metadata from action if present and merge into Step
                # This allows result handler steps to be configured via step_metadata parameter:
                #   step.on(condition,
                #       utils.echo(data=..., step_metadata=StepMetadata(
                #           key="my_step",
                #           output_behavior={"field": OutputBehaviorType.MERGE}
                #       ))
                #   )
                step_config = _extract_step_config_from_action(action)
                step_actions.append(Step(**step_config))

        # Create a result handler and add it to this step
        handler = ResultHandler(
            type=handler_type,
            if_conditions=condition,
            steps=step_actions,
        )
        self.result_handlers.append(handler)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format expected by backend."""
        # Process decorator handlers before serialization
        self._process_decorator_handlers()

        # Use model_dump but exclude problematic circular reference fields
        result = self.model_dump(
            exclude={
                "agent",
                "result_handler",
                "_decorator_handlers",
                "action",
                "depends_on",
            },
        )

        # Filter out empty/None optional fields to match export behavior
        if result.get("ui_content_type") in [None, ""]:
            result.pop("ui_content_type", None)
        if result.get("history_content_type") in [None, ""]:
            result.pop("history_content_type", None)
        if result.get("parameter_hydration_behaviour") is None:
            result.pop("parameter_hydration_behaviour", None)

        # Add action information without circular references
        result["action_type"] = self.get_action_type()
        result["parameters"] = self.extract_action_parameters()

        # Add depends_on only if there are actual dependencies
        if self.depends_on:
            # Convert Step objects to their keys
            deps = []
            for dep in self.depends_on:
                if isinstance(dep, Step):
                    # If it's a Step object, use its key
                    if dep.key:
                        deps.append(dep.key)
                elif isinstance(dep, str):
                    # If it's already a string (step key), use it directly
                    deps.append(dep)
            result["depends_on"] = deps

        # Always include result_handlers, even if they were excluded by exclude_unset
        # This ensures that result handlers added via .on() method are included
        result["result_handlers"] = []
        if self.result_handlers:
            converted_handlers: List[Any] = []
            for handler in self.result_handlers:
                if hasattr(handler, "to_dict"):
                    converted_handlers.append(handler.to_dict())
                elif isinstance(handler, dict):
                    # Already a dict, convert conditions if needed
                    handler_dict = cast(Dict[str, Any], handler)
                    if handler_dict.get("if_conditions") and hasattr(
                        handler_dict["if_conditions"], "to_dict"
                    ):
                        handler_dict["if_conditions"] = handler_dict[
                            "if_conditions"
                        ].to_dict()
                    converted_handlers.append(handler_dict)
                else:
                    converted_handlers.append(handler)
            result["result_handlers"] = converted_handlers

        # Convert ExecutionMode objects to dictionaries
        if self.execution_mode is not None:
            if hasattr(self.execution_mode, "to_dict") and callable(
                getattr(self.execution_mode, "to_dict")
            ):
                exec_mode_obj = cast(ExecutionModeProtocol, self.execution_mode)
                result["execution_mode"] = exec_mode_obj.to_dict()
            elif isinstance(self.execution_mode, dict):
                result["execution_mode"] = self.execution_mode
            else:
                # Handle string mode types or other formats
                result["execution_mode"] = self.execution_mode

        # Recursively convert any other condition objects to dictionaries
        def convert_conditions(obj: Any) -> Any:
            """Recursively convert condition objects to dictionaries."""

            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, Enum):
                # Convert enum values to their string values for JSON serialization
                return obj.value
            elif hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif isinstance(obj, list):
                return [convert_conditions(item) for item in obj]
            elif isinstance(obj, dict):
                # Handle enum keys in dictionaries
                converted_dict: Dict[str, Any] = {}
                obj_dict = cast(Dict[Any, Any], obj)
                for key, value in obj_dict.items():
                    # Convert enum keys to strings
                    str_key: str
                    if isinstance(key, Enum):
                        str_key = str(key.value)
                    else:
                        str_key = str(key)
                    converted_dict[str_key] = convert_conditions(value)
                return converted_dict
            else:
                return obj

        # Apply condition conversion to all fields
        for key, value in result.items():
            result[key] = convert_conditions(value)

        # Rename output_behavior to output_behaviour for Go backend compatibility
        # Python SDK uses American spelling (output_behavior) but Go backend expects
        # British spelling (output_behaviour). This ensures correct serialization.
        if "output_behavior" in result:
            result["output_behaviour"] = result.pop("output_behavior")

        # Recursively sort all dictionaries for deterministic serialization
        def sort_dict_recursively(obj: Any) -> Any:
            """Recursively sort all dictionaries to ensure deterministic JSON output."""
            if isinstance(obj, dict):
                # Convert keys to strings for sorting to handle mixed types (enums + strings)
                def sort_key(item: Tuple[Any, Any]) -> str:
                    k, v = item
                    if hasattr(k, "value"):  # Enum
                        return str(k.value)
                    return str(k)

                obj_dict = cast(Dict[Any, Any], obj)
                return dict(
                    sorted(
                        ((k, sort_dict_recursively(v)) for k, v in obj_dict.items()),
                        key=sort_key,
                    )
                )
            elif isinstance(obj, list):
                return [sort_dict_recursively(item) for item in obj]
            else:
                return obj

        result = sort_dict_recursively(result)
        return cast(Dict[str, Any], result)

    def _process_decorator_handlers(self) -> None:
        """Process decorator handlers and convert them to ResultHandler objects."""
        if not hasattr(self, "_decorator_handlers") or not self._decorator_handlers:
            return

        # Get current result_handlers list or create new one
        current_handlers = list(self.result_handlers) if self.result_handlers else []

        for condition, _ in self._decorator_handlers:
            # Create a simple handler that calls the function
            # For now, we'll create a basic handler structure
            # In a full implementation, you'd want to analyze the function and create
            # appropriate steps
            handler = ResultHandler(
                type=HandlerType.FINAL,
                if_conditions=condition,
                output_content_type=OutputContentType.TEXT,
                steps=[],  # Would need to convert function to steps
            )
            current_handlers.append(handler)

        # Update the result_handlers field
        self.result_handlers = current_handlers

        # Clear processed handlers
        self._decorator_handlers.clear()


class StepOutput(BaseModel):
    """Represents the output of a step for type-safe access."""

    step_key: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Use object attribute instead of Pydantic field
        object.__setattr__(self, "_expected_fields", {})

    def __getitem__(self, key: str) -> str:
        """Allow bracket notation for accessing output fields."""
        # Track that this field is being accessed for validation
        if hasattr(self, "_expected_fields"):
            expected_fields = getattr(self, "_expected_fields", {})
            expected_fields[key] = (
                None  # Will be populated with actual type during execution
            )
        return f"{{{{{self.step_key}.{key}}}}}"

    def __getattr__(self, name: str) -> str:
        """Allow dot notation for accessing output fields."""
        # Avoid infinite recursion for Pydantic internal attributes
        if name.startswith("_") or name in {"step_key", "model_fields", "model_config"}:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        # Track that this field is being accessed for validation
        if hasattr(self, "_expected_fields"):
            expected_fields = getattr(self, "_expected_fields", {})
            expected_fields[name] = (
                None  # Will be populated with actual type during execution
            )
        return f"{{{{{self.step_key}.{name}}}}}"

    def get_expected_fields(self) -> Dict[str, Any]:
        """Get the fields that have been accessed on this step output."""
        return getattr(self, "_expected_fields", {})

    def validate_field_access(self, available_fields: Dict[str, Any]) -> List[str]:
        """Validate that all accessed fields are available in the step result."""
        errors = []
        expected = self.get_expected_fields()

        for field_name in expected.keys():
            if field_name not in available_fields:
                errors.append(
                    f"Step '{self.step_key}' output field '{field_name}' is not available"
                )

        return errors


class ResultHandler(BaseModel):
    """Result handler definition that matches the Go backend structure."""

    type: HandlerType = HandlerType.FINAL
    if_conditions: Optional[Any] = None  # Can be condition objects or None
    output_content_type: OutputContentType = OutputContentType.TEXT
    history_content_type: Optional[str] = None
    ui_content_type: Optional[str] = None
    steps: List[Step] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format expected by backend."""
        # Convert Step objects in steps list to dictionaries BEFORE model_dump()
        # because model_dump() will convert Step objects to dicts but won't call to_dict()
        converted_steps = []
        if self.steps:
            for step in self.steps:
                if hasattr(step, "to_dict"):
                    step_dict = step.to_dict()
                    # DO NOT auto-generate keys for result handler steps
                    # Only include keys if explicitly set to preserve roundtrip
                    # parity

                    # Ensure bot_output_visibility is preserved (defaults to hidden for
                    # result handler steps)
                    if "bot_output_visibility" not in step_dict:
                        step_dict["bot_output_visibility"] = "hidden"

                    converted_steps.append(step_dict)
                else:
                    # Convert step to dict if it doesn't have to_dict method
                    if isinstance(step, dict):
                        converted_steps.append(step)
                    else:
                        # Fallback: convert to dict using model_dump if available
                        if hasattr(step, "model_dump"):
                            converted_steps.append(step.model_dump())
                        else:
                            converted_steps.append({})

        # Use model_dump but exclude steps, then add our properly converted steps
        result = self.model_dump(exclude={"steps"})
        result["steps"] = converted_steps

        # Filter out empty/None optional fields to match export behavior
        if result.get("ui_content_type") in [None, ""]:
            result.pop("ui_content_type", None)
        if result.get("history_content_type") in [None, ""]:
            result.pop("history_content_type", None)
        if result.get("parameter_hydration_behaviour") is None:
            result.pop("parameter_hydration_behaviour", None)

        # Convert condition objects to dictionaries if needed
        if self.if_conditions is not None and hasattr(self.if_conditions, "to_dict"):
            result["if_conditions"] = self.if_conditions.to_dict()

        # Convert enum values to their string values (both keys and values)
        converted_result = {}
        for key, value in result.items():
            # Convert enum keys to strings
            if isinstance(key, Enum):
                key = key.value
            # Convert enum values to strings
            if isinstance(value, Enum):
                value = value.value
            converted_result[key] = value
        result = converted_result

        return result


class SecretsDict(Dict[str, Any]):
    """A dictionary wrapper that provides .get() method for secrets access."""

    def __init__(self, secrets_data: Optional[Dict[str, Any]] = None):
        super().__init__(secrets_data or {})

    def get(self, key: str, default: Any = None) -> Any:
        """Get decrypted secrets for a specific resource/service key."""
        return super().get(key, default)


class ParametersDict(Dict[str, Any]):
    """A dictionary wrapper that provides .get() method for parameters access."""

    def __init__(self, parameters_data: Optional[Dict[str, Any]] = None):
        super().__init__(parameters_data or {})

    def get(self, key: str, default: Any = None) -> Any:
        """Get a step parameter with optional default."""
        return super().get(key, default)


class StepContext(BaseModel):
    """Context available to step functions with type-safe access

    Provides access to:
    - User query and parameters
    - Previous step results (state)
    - Available resources (datasets, APIs)
    - Encrypted secrets
    - System information
    """

    # Core user input
    query: Optional[str] = None

    # Previous step results and state
    state: Dict[str, Any] = Field(default_factory=dict)
    steps: Dict[str, Any] = Field(default_factory=dict)  # Alias for state.steps

    # Resources and data access
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    resource_definitions: Optional[Dict[str, Any]] = None

    # Security and credentials - raw data
    secrets_data: Dict[str, Any] = Field(default_factory=dict)

    # Step-specific parameters - raw data
    parameters_data: Dict[str, Any] = Field(default_factory=dict)

    # System context
    system: Dict[str, Any] = Field(default_factory=dict)

    # Raw context for advanced users
    raw: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        # Extract secrets and parameters from input data
        secrets_data = data.pop("secrets", {})
        parameters_data = data.pop("parameters", {})

        # Set the internal data fields
        data["secrets_data"] = secrets_data
        data["parameters_data"] = parameters_data

        super().__init__(**data)

        # Create wrapper objects for secrets and parameters
        self._secrets_wrapper = SecretsDict(self.secrets_data)
        self._parameters_wrapper = ParametersDict(self.parameters_data)

    @property
    def secrets(self) -> SecretsDict:
        """Get secrets wrapper that supports .get() method."""
        return self._secrets_wrapper

    @property
    def parameters(self) -> ParametersDict:
        """Get parameters wrapper that supports .get() method."""
        return self._parameters_wrapper

    def __getitem__(self, key: str) -> Any:
        """Allow bracket notation access to state"""
        try:
            state_value = super().__getattribute__("state")
            return state_value.get(key) if isinstance(state_value, dict) else None
        except AttributeError:
            return None

    def __getattr__(self, name: str) -> Any:
        """Allow dot notation access to state"""
        # Avoid infinite recursion for Pydantic internal attributes
        if name.startswith("_") or name in {
            "state",
            "steps",
            "resources",
            "secrets",
            "parameters",
            "system",
            "raw",
            "query",
            "resource_definitions",
        }:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        try:
            state_value = super().__getattribute__("state")
            if isinstance(state_value, dict) and name in state_value:
                return state_value[name]
        except AttributeError:
            pass
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def get_resource(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by key"""
        for resource in self.resources:
            if resource.get("key") == key:
                return resource
        return None

    def get_secret(self, key: str) -> Optional[Any]:
        """Get decrypted secrets for a specific resource/service"""
        return self.secrets.get(key)

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a step parameter with optional default"""
        return self.parameters.get(key, default)


class StepResult(BaseModel):
    """Result from executing a workflow step."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    step_name: str


class Agent(BaseModel):
    """Main agent class for defining AI workflows."""

    name: str
    key: Optional[str] = None
    description: Optional[str] = None
    persona: Optional[str] = None
    visibility: str = "public"
    running_message: Optional[Union[str, TemplateString]] = None
    finished_message: Optional[Union[str, TemplateString]] = None
    version: str = "1.0"
    timeout: Optional[int] = None
    retry_attempts: int = 0
    tags: List[str] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)
    parameter_definitions: List["ParameterDefinition"] = Field(default_factory=list)

    @field_serializer(
        "running_message", "finished_message", mode="wrap", when_used="always"
    )
    def serialize_message_fields(
        self, value: Optional[Union[str, TemplateString]], _info
    ) -> Optional[str]:
        """Convert TemplateString to str during serialization."""
        if isinstance(value, TemplateString):
            return str(value)
        return value

    def step(
        self,
        action: Any,
        key: Optional[str] = None,
        depends_on: Optional[Union[Step, List[Step], str, List[str]]] = None,
        **kwargs: Any,
    ) -> Step:
        """Create a step with cleaner syntax and better defaults.

        Args:
            action: The action to execute (e.g., codeexec.execute(...))
            key: Optional step key, auto-generated if not provided
            depends_on: Step(s) or key(s) this step depends on
            **kwargs: Additional step configuration

        Returns:
            Step: The created step with sensible defaults
        """
        # Extract step_metadata from the action if present
        extracted_config = _extract_step_config_from_action(action)

        # Auto-generate key if not provided (either via param or step_metadata)
        if key is None and "key" not in extracted_config:
            key = f"step_{len(self.steps) + 1}"

        # Set sensible defaults
        step_config = {
            "agent": self,
            "key": key,
            "action": action,
            "depends_on": (
                [depends_on]
                if depends_on and not isinstance(depends_on, list)
                else depends_on
            ),
            "user_output_visibility": OutputVisibility.VISIBLE,
            "bot_output_visibility": OutputVisibility.HIDDEN,
            "output_content_type": OutputContentType.TEXT,
        }

        # First merge extracted_config (from step_metadata), then kwargs
        # This allows kwargs to override step_metadata if needed
        step_config.update(extracted_config)
        step_config.update(kwargs)

        step = Step(**step_config)
        return step

    def exec(
        self,
        step_metadata: Optional[StepMetadata] = None,
        **codeexec_params: Any,
    ) -> Callable[..., Step]:
        """Create a codeexec step using decorator syntax.

        This method is designed to be used as a decorator for functions that implement
        code execution logic. It creates a codeexec.execute action with the provided
        parameters and step metadata.

        Args:
            step_metadata: Step configuration (key, depends_on, etc.)
            **codeexec_params: Parameters for codeexec.execute (entrypoint, parameters,
                resources, etc.)

        Returns:
            Callable: Decorator function that creates and returns a Step
        """

        def decorator(func: Callable[..., Any]) -> Step:
            # Import here to avoid circular imports
            from .actions import codeexec

            # Create the codeexec.execute action with the provided parameters
            action = codeexec.execute(**codeexec_params)

            # Extract step metadata or use defaults
            if step_metadata:
                step_config = {
                    "agent": self,
                    "action": action,
                    "key": step_metadata.key or func.__name__,
                    "depends_on": step_metadata.depends_on,
                    "execution_mode": step_metadata.execution_mode,
                    "output_behavior": step_metadata.output_behavior,
                    "output_channels": step_metadata.output_channels,
                    "output_content_type": step_metadata.output_content_type,
                    "history_content_type": step_metadata.history_content_type,
                    "ui_content_type": step_metadata.ui_content_type,
                    "user_output_visibility": step_metadata.user_output_visibility,
                    "bot_output_visibility": step_metadata.bot_output_visibility,
                    "running_message": step_metadata.running_message,
                    "finished_message": step_metadata.finished_message,
                    "parameter_hydration_behaviour": step_metadata.parameter_hydration_behaviour,
                }
            else:
                step_config = {
                    "agent": self,
                    "action": action,
                    "key": func.__name__,
                    "user_output_visibility": OutputVisibility.VISIBLE,
                    "bot_output_visibility": OutputVisibility.HIDDEN,
                    "output_content_type": OutputContentType.TEXT,
                }

            # Remove None values and extract action separately
            filtered_config = {
                k: v for k, v in step_config.items() if v is not None and k != "action"
            }

            # Create step with the codeexec action, not the function
            step = Step(action=action, step=None, **filtered_config)

            # Store the function name on the step for runtime extraction
            if hasattr(step, "__dict__"):
                step.__dict__["__name__"] = func.__name__

            return step

        return decorator

    def add_step(self, step: Step) -> None:
        """Add a step to this agent if it's not already present."""
        # Only add if the step is not already in the list
        if step in self.steps:
            return

        # Create a new list with the existing steps plus the new one
        current_steps = list(self.steps) if self.steps else []
        current_steps.append(step)
        self.steps = current_steps

    def get_step(self, key: str) -> Optional[Step]:
        """Get a step by its key."""
        for step in self.steps:
            if step.key == key:
                return step
        return None

    def to_json(self) -> str:
        """Export to JSON format expected by Go backend."""
        export_data = {
            "bot": {
                "Name": self.name,
                "Key": self.key,
                "Description": self.description or "",
                "Visibility": self.visibility,
                "Persona": self.persona,  # Export as string or null, not object
                "RunningMessage": self.running_message,
                "FinishedMessage": self.finished_message,
                "Source": "python",
            },
            "parameter_definitions": self.parameter_definitions,
            "steps": [step.to_dict() for step in self.steps],
        }

        import json

        return json.dumps(export_data, indent=2)


class ExecutionMode(BaseModel):
    """Execution mode matching Go backend structure."""

    mode: ExecutionModeType = ExecutionModeType.ALL
    data: Optional[Any] = None
    if_condition: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format expected by backend."""
        result: Dict[str, Any] = {"mode": self.mode}
        if self.data is not None:
            result["data"] = self.data
        # Always include if_condition to maintain parity with backend structure
        result["if_condition"] = self.if_condition
        return result


class Prompt(BaseModel):
    """A prompt that can be loaded from a .prompt file or defined inline.

    This class provides a clean way to manage prompts in agent code,
    supporting both inline strings and external .prompt files.
    """

    content: str = Field(..., description="The prompt content")
    filename: Optional[str] = Field(
        None, description="Source filename if loaded from file"
    )

    def __init__(
        self, content: Optional[str] = None, filename: Optional[str] = None, **data: Any
    ):
        """Initialize a Prompt.

        Args:
            content: Direct prompt content
            filename: Path to .prompt file to load
            **data: Additional model data
        """
        if content is not None and filename is not None:
            raise ValueError("Cannot specify both 'content' and 'filename' parameters")

        if content is None and filename is None:
            raise ValueError("Must specify either 'content' or 'filename' parameter")

        if filename is not None:
            # Load content from file
            content = self._load_from_file(filename)
            data.update({"content": content, "filename": filename})
        else:
            data.update({"content": content})

        super().__init__(**data)

    @classmethod
    def from_file(cls, filename: str, base_path: Optional[str] = None) -> "Prompt":
        """Load a prompt from a .prompt file.

        Args:
            filename: Path to the .prompt file
            base_path: Base directory to resolve relative paths (defaults to cwd)

        Returns:
            Prompt: Loaded prompt instance
        """
        if base_path is None:
            base_path = os.getcwd()

        file_path = Path(base_path) / filename

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return cls(content=content)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading prompt file {file_path}: {e}")

    def _load_from_file(self, filename: str) -> str:
        """Load content from a .prompt file."""
        return self.from_file(filename).content

    def __str__(self) -> str:
        """Return the prompt content when used as a string."""
        return self.content

    def __call__(self) -> str:
        """Allow the prompt to be called like a function, returning content."""
        return self.content

    def __repr__(self) -> str:
        """Return a helpful representation."""
        if self.filename:
            return f"Prompt(filename='{self.filename}')"
        else:
            preview = (
                self.content[:50] + "..." if len(self.content) > 50 else self.content
            )
            return f"Prompt(content='{preview}')"

    @classmethod
    def load_from_directory(
        cls, directory: str, base_path: Optional[str] = None
    ) -> Dict[str, "Prompt"]:
        """Load all .prompt files from a directory as Prompt objects.

        Args:
            directory: Directory containing .prompt files
            base_path: Base directory to resolve relative paths (defaults to smart detection)

        Returns:
            Dict[str, Prompt]: Mapping of filename (without extension) to Prompt objects
        """
        if base_path is None:
            # Use stack inspection to determine the calling file's directory
            # This allows agents to load prompts from their own directory
            # even when executed from a different working directory
            import inspect

            frame = inspect.currentframe()
            try:
                # Get the caller's frame (skip current frame)
                if frame and frame.f_back:
                    caller_frame = frame.f_back
                    caller_file = caller_frame.f_code.co_filename
                    caller_dir = Path(caller_file).parent
                    # Check if the caller is in an agent directory structure
                    # (i.e., the calling file is agent.py in a directory under erdo-agents)
                    if caller_file.endswith("agent.py") and "erdo-agents" in str(
                        caller_dir
                    ):
                        # The caller is an agent.py file, use its directory
                        base_path = str(caller_dir)
                    else:
                        # Fall back to current working directory
                        base_path = os.getcwd()
                else:
                    # Fall back to current working directory
                    base_path = os.getcwd()
            finally:
                del frame  # Avoid reference cycles

        dir_path = Path(base_path) / directory

        if not dir_path.exists() or not dir_path.is_dir():
            # Provide a more helpful error message
            cwd = os.getcwd()
            caller_path = None
            import inspect

            frame = inspect.currentframe()
            try:
                if frame and frame.f_back:
                    caller_file = frame.f_back.f_code.co_filename
                    caller_path = str(Path(caller_file).parent)
            finally:
                del frame

            error_msg = f"Prompts directory not found: {dir_path}"
            if caller_path and caller_path != str(Path(base_path)):
                error_msg += f"\nCalling file: {caller_path}"
            error_msg += f"\nCurrent working directory: {cwd}"
            error_msg += f"\nBase path used: {base_path}"
            raise FileNotFoundError(error_msg)

        prompts = {}
        for prompt_file in dir_path.glob("*.prompt"):
            prompt_name = prompt_file.stem  # filename without extension
            relative_path = str(prompt_file.relative_to(base_path))
            prompts[prompt_name] = cls.from_file(relative_path, base_path)

        return prompts


class ConditionDefinition(BaseModel):
    """Condition definition for test expectations."""

    type: str  # "TextContains", "IsSuccess", etc.
    path: str  # JSONPath or template path to value
    parameters: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format expected by backend."""
        return {"type": self.type, "path": self.path, "parameters": self.parameters}


class APIConditionDefinition(BaseModel):
    """API condition definition that matches backend expectations."""

    type: str  # "TextContains", "IsSuccess", etc.
    conditions: List[Any] = Field(default_factory=list)  # For composite conditions
    leaf: Dict[str, Any] = Field(default_factory=dict)  # Parameters for leaf conditions

    @field_serializer("leaf")
    def serialize_leaf(self, leaf_data: Dict[str, Any]) -> str:
        """Serialize leaf field as JSON string to match Go backend json.RawMessage expectation."""
        import json

        if leaf_data:
            # Convert TemplateString objects to strings
            converted_leaf = {}
            for key, value in leaf_data.items():
                if hasattr(value, "template"):  # This is a TemplateString
                    converted_leaf[key] = value.template
                else:
                    converted_leaf[key] = value
            return json.dumps(converted_leaf)
        else:
            # Even if leaf is empty, ensure it's a JSON string
            return "{}"


# Re-export commonly used types for convenience
__all__ = [
    "Agent",
    "Step",
    "StepMetadata",
    "StepContext",
    "StepResult",
    "StepOutput",
    "ResultHandler",
    "ExecutionMode",
    "Tool",
    "PythonFile",
    "Prompt",
    "TemplateString",
    # Complex types
    "ExecutionCondition",
    "ConditionDefinition",
    # Resource types
    "BotResource",
    "Dataset",
    "DatasetType",
    # Bot permissions
    "BotPermissions",
    "set_bot_public",
    "set_bot_user_permission",
    "set_bot_org_permission",
    "get_bot_permissions",
    "check_bot_access",
]
