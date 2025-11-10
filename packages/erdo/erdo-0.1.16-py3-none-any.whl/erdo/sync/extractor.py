"""Runtime extraction for syncing agents to the backend."""

import ast
import importlib.util
import inspect
import json
import os
import sys
import textwrap
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class TemplateStringEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles TemplateString objects and enums."""

    def default(self, obj):
        if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            return obj.to_dict()
        elif str(type(obj).__name__) == "TemplateString":
            if hasattr(obj, "to_template_string") and callable(
                getattr(obj, "to_template_string")
            ):
                return obj.to_template_string()
            elif hasattr(obj, "template"):
                return obj.template
            else:
                return str(obj)
        elif hasattr(obj, "__class__") and hasattr(obj.__class__, "__mro__"):
            for base in obj.__class__.__mro__:
                if "Enum" in str(base):
                    return obj.value if hasattr(obj, "value") else str(obj)
        elif hasattr(obj, "_parent_path"):
            return str(obj)
        return super().default(obj)


def transform_string_value(value: str) -> str:
    """Transform a string value by converting state.field to {{.Data.field}} templates."""
    if not isinstance(value, str):
        return value

    import re

    pattern = r"\bstate\.([a-zA-Z_][a-zA-Z0-9_.]*)"

    def replace_state_ref(match):
        field_path = match.group(1)
        return "{{.Data." + field_path + "}}"

    transformed = re.sub(pattern, replace_state_ref, value)
    return transformed


def transform_dict_recursively(obj: Any) -> Any:
    """Recursively transform a dictionary/object, converting state references to templates."""
    if hasattr(obj, "_parent_path") and hasattr(obj, "_tracker"):
        field_path = obj._parent_path
        return "{{.Data." + field_path + "}}"
    elif (
        hasattr(obj, "to_dict")
        and hasattr(obj, "filename")
        and "PythonFile" in str(type(obj))
    ):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: transform_dict_recursively(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [transform_dict_recursively(item) for item in obj]
    elif isinstance(obj, str):
        return transform_string_value(obj)
    elif hasattr(obj, "__class__") and hasattr(obj.__class__, "__mro__"):
        # Handle enums by converting to their value
        for base in obj.__class__.__mro__:
            if "Enum" in str(base):
                return obj.value if hasattr(obj, "value") else str(obj)
        return obj
    else:
        return obj


def convert_step_dict_to_step_with_handlers(step_dict: Dict) -> Dict:
    """Convert a step dictionary to StepWithHandlers format recursively."""
    step_data = dict(step_dict)
    result_handlers_list = step_data.pop("result_handlers", [])
    converted_result_handlers = []

    for handler in result_handlers_list:
        converted_handler = dict(handler)

        if "steps" in converted_handler and isinstance(
            converted_handler["steps"], list
        ):
            converted_steps = []
            for step in converted_handler["steps"]:
                if hasattr(step, "to_dict"):
                    converted_step = convert_step_to_step_with_handlers(step)
                else:
                    converted_step = convert_step_dict_to_step_with_handlers(step)
                converted_steps.append(converted_step)
            converted_handler["steps"] = converted_steps

        converted_result_handlers.append(converted_handler)

    return {
        "step": step_data,
        "result_handlers": converted_result_handlers,
    }


def get_all_python_files_in_directory(
    source_file_path: str, exclude_patterns: Optional[List[str]] = None
) -> List[Dict]:
    """Get all Python files in the same directory as the source file."""
    if exclude_patterns is None:
        exclude_patterns = ["__pycache__", "*.pyc", "test_*", "*_test.py"]

    import fnmatch

    source_dir = Path(source_file_path).parent
    files = []

    for py_file in source_dir.glob("*.py"):
        if py_file.samefile(source_file_path):
            continue

        if any(fnmatch.fnmatch(py_file.name, pattern) for pattern in exclude_patterns):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            files.append({"filename": py_file.name, "content": content})
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}", file=sys.stderr)

    return files


def resolve_code_files_references(
    code_files: List, source_file_path: str
) -> List[Dict]:
    """Resolve PythonFile references to actual file contents."""
    if not code_files:
        return []

    resolved_files = []
    source_dir = Path(source_file_path).parent

    for file_ref in code_files:
        if isinstance(file_ref, dict) and file_ref.get("_type") == "PythonFile":
            filename_with_path = file_ref["filename"]
            file_path = source_dir / filename_with_path

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                base_filename = Path(filename_with_path).name
                resolved_files.append({"filename": base_filename, "content": content})
            except Exception as e:
                print(
                    f"Warning: Could not resolve PythonFile {file_path}: {e}",
                    file=sys.stderr,
                )
        else:
            resolved_files.append(file_ref)

    return resolved_files


def extract_and_update_function_code(
    step_obj: Any, step_dict: Dict, source_file_path: str
):
    """Extract function body from decorated codeexec.execute function and update step parameters."""
    func_name = getattr(step_obj, "__name__", None)
    if not func_name:
        return

    try:
        with open(source_file_path, "r") as f:
            source_content = f.read()

        tree = ast.parse(source_content)
        func_body = None

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                source_lines = source_content.split("\n")
                start_line = node.lineno
                end_line = (
                    node.end_lineno
                    if hasattr(node, "end_lineno")
                    else len(source_lines)
                )
                body_lines = source_lines[start_line:end_line]
                func_body = textwrap.dedent("\n".join(body_lines))
                break

        if func_body:
            if "parameters" not in step_dict:
                step_dict["parameters"] = {}

            existing_code_files = step_dict["parameters"].get("code_files", [])
            resolved_files = resolve_code_files_references(
                existing_code_files, source_file_path
            )
            directory_files = get_all_python_files_in_directory(source_file_path)
            resolved_files.extend(directory_files)

            main_content = f"""# Function: {func_name}
import json
import sys
import os
from erdo.types import StepContext

def {func_name}(context):
    \"\"\"Extracted function implementation.\"\"\"
{textwrap.indent(func_body, '    ')}

if __name__ == "__main__":
    parameters_json = os.environ.get('STEP_PARAMETERS', '{{}}')
    parameters = json.loads(parameters_json)
    secrets_json = os.environ.get('STEP_SECRETS', '{{}}')
    secrets = json.loads(secrets_json)
    context = StepContext(parameters=parameters, secrets=secrets)

    try:
        result = {func_name}(context)
        if result:
            print(json.dumps(result))
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        sys.exit(1)
"""

            all_files = [{"filename": "main.py", "content": main_content}]
            all_files.extend(resolved_files)

            seen_filenames = set()
            unique_files = []
            for file_dict in all_files:
                filename = file_dict.get("filename")
                if filename and filename not in seen_filenames:
                    seen_filenames.add(filename)
                    unique_files.append(file_dict)

            step_dict["parameters"]["code_files"] = unique_files

    except Exception as e:
        print(f"Warning: Failed to extract function {func_name}: {e}", file=sys.stderr)


def convert_step_to_step_with_handlers(
    step_obj: Any, source_file_path: Optional[str] = None
) -> Dict:
    """Convert a Step object to StepWithHandlers format recursively."""
    step_dict = step_obj.to_dict()
    step_dict = transform_dict_recursively(step_dict)

    if source_file_path and step_dict.get("parameters", {}).get("code_files"):
        existing_code_files = step_dict["parameters"]["code_files"]
        resolved_files = resolve_code_files_references(
            existing_code_files, source_file_path
        )
        if resolved_files:
            step_dict["parameters"]["code_files"] = resolved_files

    if (
        source_file_path
        and hasattr(step_obj, "__name__")
        and not any(
            file_dict.get("content")
            for file_dict in step_dict.get("parameters", {}).get("code_files", [])
        )
    ):
        try:
            extract_and_update_function_code(step_obj, step_dict, source_file_path)
        except Exception:
            pass

    return convert_step_dict_to_step_with_handlers(step_dict)


def extract_action_result_schemas(module: Any) -> Dict:
    """Extract action result schemas from parameter classes with _result attribute."""
    result_schemas = {}

    for name in dir(module):
        obj = getattr(module, name)
        if inspect.isclass(obj) and hasattr(obj, "_result"):
            result_class = obj._result
            if not inspect.isclass(result_class):
                continue

            action_name = None
            if hasattr(obj, "model_fields"):
                name_field = obj.model_fields.get("name")
                if name_field and name_field.default:
                    action_name = name_field.default.split(".")[-1]
            elif hasattr(obj, "__fields__"):
                name_field = obj.__fields__.get("name")
                if name_field and name_field.default:
                    action_name = name_field.default.split(".")[-1]

            if action_name and result_class:
                schema: Dict[str, Any] = {
                    "class_name": result_class.__name__,
                    "description": result_class.__doc__ or "",
                    "required_fields": [],
                    "optional_fields": [],
                    "field_types": {},
                }

                fields = {}
                if hasattr(result_class, "model_fields"):
                    fields = result_class.model_fields
                elif hasattr(result_class, "__fields__"):
                    fields = result_class.__fields__

                for field_name, field_info in fields.items():
                    is_required = True
                    if hasattr(field_info, "is_required"):
                        is_required = field_info.is_required()
                    elif hasattr(field_info, "required"):
                        is_required = field_info.required
                    elif (
                        hasattr(field_info, "default")
                        and field_info.default is not None
                    ):
                        is_required = False

                    if is_required:
                        schema["required_fields"].append(field_name)
                    else:
                        schema["optional_fields"].append(field_name)

                    field_type = "any"
                    if hasattr(field_info, "annotation"):
                        annotation = field_info.annotation
                        if annotation == str:
                            field_type = "string"
                        elif annotation == int:
                            field_type = "number"
                        elif annotation == bool:
                            field_type = "boolean"
                        elif annotation == list:
                            field_type = "array"
                        elif annotation == dict:
                            field_type = "object"

                    schema["field_types"][field_name] = field_type

                result_schemas[action_name] = schema

    return result_schemas


def extract_single_agent_data(
    agent: Any, file_path: str, module: Optional[Any] = None
) -> Dict:
    """Extract data from a single agent."""
    steps = getattr(agent, "steps", [])
    step_dicts = []

    for step in steps:
        step_with_handlers = convert_step_to_step_with_handlers(step, file_path)

        if hasattr(step, "_module_files") and step._module_files:
            step_dict = step_with_handlers["step"]
            if "parameters" not in step_dict:
                step_dict["parameters"] = {}

            code_files = []
            for fp, content in step._module_files.items():
                code_files.append({"filename": fp, "content": content})

            step_dict["parameters"]["code_files"] = code_files
            if hasattr(step, "_entrypoint"):
                step_dict["parameters"]["entrypoint"] = step._entrypoint

        step_dicts.append(step_with_handlers)

    action_result_schemas = {}
    if module:
        action_result_schemas = extract_action_result_schemas(module)

    source_code = ""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r") as f:
            source_code = f.read()

    return {
        "bot": {
            "name": agent.name,
            "key": getattr(agent, "key", None),  # Include the bot key
            "description": agent.description or "",
            "visibility": agent.visibility,
            "persona": agent.persona,
            "running_message": agent.running_message,
            "finished_message": agent.finished_message,
            "source": "python",
        },
        "parameter_definitions": agent.parameter_definitions or [],
        "steps": step_dicts,
        "file_path": file_path,
        "source_code": source_code,
        "action_result_schemas": action_result_schemas,
    }


def extract_agent_from_instance(
    agent: Any, source_file_path: Optional[str] = None
) -> Dict:
    """Extract agent data from an Agent instance."""
    if source_file_path:
        # Try to load the module to get action schemas
        try:
            spec = importlib.util.spec_from_file_location(
                "agent_module", source_file_path
            )
            if not spec or not spec.loader:
                raise ValueError(f"Could not load module spec from {source_file_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            module = None
    else:
        module = None

    return extract_single_agent_data(agent, source_file_path or "", module)


def extract_agents_from_file(file_path: str) -> Union[Dict, List[Dict]]:
    """Extract agent(s) from a Python file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File does not exist: {file_path}")

    # Check if file has agents
    with open(file_path, "r") as f:
        source = f.read()

    tree = ast.parse(source)
    has_agents = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "agents":
                    has_agents = True
                    break

    if not has_agents:
        raise ValueError("No 'agents = [...]' assignment found in file")

    # Load the module
    file_dir = os.path.dirname(file_path)
    if file_dir not in sys.path:
        sys.path.insert(0, file_dir)

    spec = importlib.util.spec_from_file_location("target_module", file_path)
    if not spec or not spec.loader:
        raise ValueError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        spec.loader.exec_module(module)

    if not hasattr(module, "agents"):
        raise ValueError("No 'agents' list found in the module")

    agents_list = getattr(module, "agents")
    if not isinstance(agents_list, list) or len(agents_list) == 0:
        raise ValueError("'agents' must be a non-empty list")

    # Check if we're extracting all agents or just one
    if len(agents_list) > 1 and file_path.endswith("__init__.py"):
        result = []
        for agent in agents_list:
            agent_data = extract_single_agent_data(agent, file_path, module)
            result.append(agent_data)
        return result
    else:
        agent = agents_list[0]
        return extract_single_agent_data(agent, file_path, module)
