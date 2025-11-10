"""
Erdo State Management

Provides a magic `state` object that allows clean Python syntax like:
- state.code
- state.dataset.id
- f"Analysis for: {state.code}"

The state object tracks field access for static analysis and template conversion.
"""

import ast
from collections import defaultdict
from typing import Any, Dict, Optional, Set

# Import template functions list - no fallback, fail fast if missing
from ._generated.template_functions import ALL_TEMPLATE_FUNCTIONS


class StateFieldTracker:
    """Tracks field access on the state object for template conversion."""

    def __init__(self):
        self.accessed_fields: Set[str] = set()
        self.nested_access: Dict[str, Set[str]] = defaultdict(set)

    def record_access(self, field_path: str) -> None:
        """Record that a state field was accessed."""
        self.accessed_fields.add(field_path)

        # Track nested access (e.g., "dataset.id" -> nested_access["dataset"].add("id"))
        parts = field_path.split(".")
        if len(parts) > 1:
            parent = parts[0]
            child = ".".join(parts[1:])
            self.nested_access[parent].add(child)


class StateMethodProxy:
    """Proxy object for state method calls like state.toJSON(x)"""

    def __init__(self, method_name: str, tracker: StateFieldTracker):
        self._method_name = method_name
        self._tracker = tracker

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Handle method calls like state.toJSON(state.security_issues)"""
        # Record that this method was called
        self._tracker.record_access(f"{self._method_name}(*args)")

        # For import-time safety, return a safe placeholder
        if self._method_name == "toJSON":
            return f"{{{{toJSON {args[0] if args else ''}}}}}"
        elif self._method_name == "len":
            return f"{{{{len {args[0] if args else ''}}}}}"
        else:
            # Generic method call placeholder
            return f"{{{{{self._method_name} {' '.join(str(arg) for arg in args)}}}}}"

    def __str__(self) -> str:
        return f"{{{{.{self._method_name}}}}}"

    def __repr__(self) -> str:
        return f"StateMethodProxy('{self._method_name}')"


class NestedStateProxy(str):
    """Proxy object for nested state access like state.dataset.id"""

    def __new__(cls, parent_path: str, tracker: StateFieldTracker):
        # Create a string with the template representation
        template_str = f"{{{{.Data.{parent_path}}}}}"
        obj = str.__new__(cls, template_str)
        obj._parent_path = parent_path
        obj._tracker = tracker
        return obj

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        field_path = f"{self._parent_path}.{name}"
        self._tracker.record_access(field_path)

        # Return another proxy for further nesting
        return NestedStateProxy(field_path, self._tracker)

    def __str__(self) -> str:
        """Convert to template string when used in f-strings."""
        # Handle special references that need .Data prefix
        if self._parent_path.startswith("steps.") or self._parent_path.startswith(
            "system."
        ):
            return f"{{{{.Data.{self._parent_path}}}}}"
        return f"{{{{{self._parent_path}}}}}"

    def __repr__(self) -> str:
        return f"NestedStateProxy('{self._parent_path}')"

    def __reduce__(self):
        """Support for pickling/serialization - return the template string."""
        return (str, (f"{{{{.Data.{self._parent_path}}}}}",))

    def __eq__(self, other: Any) -> bool:
        """Handle equality comparisons gracefully."""
        if isinstance(other, NestedStateProxy):
            return self._parent_path == other._parent_path
        return False

    def __bool__(self):
        """Handle boolean context gracefully."""
        return True

    def __hash__(self):
        """Make proxy hashable for use in dicts/sets."""
        return hash(self._parent_path)

    def __iter__(self):
        """Handle iteration attempts gracefully."""
        return iter([])

    def __len__(self):
        """Handle len() calls gracefully."""
        return 0

    def __getitem__(self, key: Any) -> "NestedStateProxy":
        """Handle indexing gracefully."""
        return NestedStateProxy(f"{self._parent_path}[{key}]", self._tracker)

    def __setattr__(self, name: str, value: Any):
        """Override setattr to allow internal attributes while tracking field access."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            # Record the assignment as a field access
            field_path = (
                f"{self._parent_path}.{name}" if hasattr(self, "_parent_path") else name
            )
            if hasattr(self, "_tracker"):
                self._tracker.record_access(field_path)


class StateMagic:
    """Magic state object that tracks field access and provides clean Python syntax."""

    def __init__(self):
        self._tracker = StateFieldTracker()
        self._test_values: Dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        """Handle attribute access like state.code, state.dataset, etc."""
        self._tracker.record_access(name)

        # Handle method calls that should return callable proxies
        if name in ALL_TEMPLATE_FUNCTIONS:
            return StateMethodProxy(name, self._tracker)

        # If we have a test value, check if it's a dict (nested object)
        if name in self._test_values:
            test_value = self._test_values[name]
            if isinstance(test_value, dict):
                # For nested objects, return a proxy that can handle further access
                proxy = NestedStateProxy(name, self._tracker)
                # Attach test data to the proxy for local testing
                proxy._test_data = test_value
                return proxy
            # For non-dict test values, still return a proxy to allow chaining
            # but it will return the string representation when accessed
            return NestedStateProxy(name, self._tracker)

        # Always return a NestedStateProxy to support nested access
        # This allows state.organization.name to work correctly
        return NestedStateProxy(name, self._tracker)

    def __str__(self) -> str:
        """When used in f-strings, this shouldn't happen (individual fields should be accessed)."""
        return "{{state}}"  # Fallback, though this should rarely be used

    def __setattr__(self, name: str, value: Any):
        """Override setattr to allow internal attributes while tracking field access."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            # Record the assignment as a field access
            self._tracker.record_access(name)
            self._test_values[name] = value

    def set_test_value(self, field_path: str, value: Any):
        """Set a test value for local development/testing."""
        parts = field_path.split(".")
        current = self._test_values

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    def get_accessed_fields(self) -> Set[str]:
        """Get all fields that have been accessed."""
        return self._tracker.accessed_fields.copy()

    def clear_tracking(self):
        """Clear the field access tracking."""
        self._tracker = StateFieldTracker()


# Global state object for use in agent definitions
state = StateMagic()


def extract_state_references_from_ast(source_code: str) -> Set[str]:
    """Extract all state.* references from Python source code using AST parsing."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return set()

    state_refs = set()

    class StateVisitor(ast.NodeVisitor):
        def visit_Attribute(self, node):
            """Visit attribute access like state.code, state.dataset.id"""
            if isinstance(node.value, ast.Name) and node.value.id == "state":
                # Simple case: state.field
                state_refs.add(node.attr)
            elif isinstance(node.value, ast.Attribute):
                # Nested case: state.dataset.id
                path = self._get_full_attribute_path(node)
                if path and path.startswith("state."):
                    # Remove 'state.' prefix
                    field_path = path[6:]
                    state_refs.add(field_path)

            self.generic_visit(node)

        def visit_JoinedStr(self, node):
            """Visit f-string expressions like f"Analysis for: {state.code}" """
            for value in node.values:
                if isinstance(value, ast.FormattedValue):
                    # Extract the expression inside the f-string
                    if isinstance(value.value, ast.Attribute):
                        path = self._get_full_attribute_path(value.value)
                        if path and path.startswith("state."):
                            field_path = path[6:]
                            state_refs.add(field_path)
                    elif (
                        isinstance(value.value, ast.Name) and value.value.id == "state"
                    ):
                        state_refs.add("state")  # Direct state reference

            self.generic_visit(node)

        def _get_full_attribute_path(self, node):
            """Get the full dotted path for an attribute access."""
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    return f"{node.value.id}.{node.attr}"
                else:
                    parent_path = self._get_full_attribute_path(node.value)
                    if parent_path:
                        return f"{parent_path}.{node.attr}"
            elif isinstance(node, ast.Name):
                return node.id
            return None

    visitor = StateVisitor()
    visitor.visit(tree)

    return state_refs


def convert_fstring_to_template(source_code: str, state_refs: Set[str]) -> str:
    """Convert f-strings with state references to Go template format."""

    class FStringConverter(ast.NodeTransformer):
        def visit_JoinedStr(self, node):
            """Convert f-strings to regular strings with Go template syntax."""
            parts = []
            has_state_ref = False

            for value in node.values:
                if isinstance(value, ast.Constant):
                    # Regular string part
                    parts.append(value.value)
                elif isinstance(value, ast.FormattedValue):
                    # Expression inside f-string
                    if isinstance(value.value, ast.Attribute):
                        path = self._get_full_attribute_path(value.value)
                        if path and path.startswith("state."):
                            # Convert state.field to {{field}}
                            field_path = path[6:]
                            parts.append(f"{{{{{field_path}}}}}")
                            has_state_ref = True
                            continue

                    # Non-state expression - convert back to string representation
                    # This is complex, so for now we'll leave it as is
                    # In practice, most f-strings in agent code should be simple state refs
                    parts.append(f"{{{ast.unparse(value.value)}}}")

            if has_state_ref:
                # Replace the f-string with a regular string
                template_str = "".join(parts)
                return ast.Constant(value=template_str)

            return node

        def _get_full_attribute_path(self, node):
            """Get the full dotted path for an attribute access."""
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    return f"{node.value.id}.{node.attr}"
                else:
                    parent_path = self._get_full_attribute_path(node.value)
                    if parent_path:
                        return f"{parent_path}.{node.attr}"
            elif isinstance(node, ast.Name):
                return node.id
            return None

    try:
        tree = ast.parse(source_code)
        converter = FStringConverter()
        new_tree = converter.visit(tree)
        return ast.unparse(new_tree)
    except Exception:
        # If conversion fails, return original
        return source_code


def validate_state_fields(
    state_refs: Set[str], available_fields: Optional[Set[str]] = None
) -> Dict[str, str]:
    """Validate that all referenced state fields are available.

    Args:
        state_refs: Set of state field references found in the code
        available_fields: Optional set of known available fields. If None, no validation is performed.

    Returns a dict of {invalid_field: error_message} for any issues.
    """
    errors: Dict[str, str] = {}

    # If no available_fields provided, skip validation (user-defined state is flexible)
    if available_fields is None:
        return errors

    for field_ref in state_refs:
        if field_ref not in available_fields:
            # Check if it's a nested field
            parts = field_ref.split(".")
            if len(parts) > 1:
                parent = parts[0]
                if parent not in available_fields:
                    errors[field_ref] = f"State field '{parent}' is not available"
                # For nested fields, assume they're valid if parent exists
                # Real validation would require schema knowledge
            else:
                errors[field_ref] = f"State field '{field_ref}' is not available"

    return errors


def setup_test_state(**test_values):
    """Setup test values for local development and testing.

    Example:
        setup_test_state(
            code="print('hello')",
            dataset={'id': 'test123', 'config': {'type': 'csv'}},
            query="analyze this data"
        )
    """
    for field_path, value in test_values.items():
        state.set_test_value(field_path, value)
