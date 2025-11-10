"""
Template string handling for export/import roundtrip compatibility.

This module provides utilities for handling template strings during the
export/import roundtrip process. Template strings are Go template expressions
that can't be executed as Python, so they need special handling.
"""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from erdo.types import Prompt


class TemplateString:
    """
    A wrapper class for template strings during export/import roundtrip.

    This class represents a Go template string (like {{.Data.field}}) in a way
    that can be executed as Python code and then converted back to the original
    template string during import.

    It implements various duck-typing methods to be compatible with Pydantic
    validation while preserving the template content for later extraction.
    """

    template: str

    def __init__(self, template: Union[str, "Prompt"]):
        """
        Initialize a TemplateString with the template content.

        Args:
            template: The template string content (e.g., "{{.Data.field}}") or a Prompt object
        """
        # Convert Prompt objects to strings, ensure template is always a string
        if hasattr(template, "content"):
            # This is a Prompt object
            self.template = str(template)
        else:
            self.template = str(template)

    def __str__(self) -> str:
        """Return the template string for display purposes."""
        return self.template

    def __repr__(self) -> str:
        """Return a representation of the TemplateString."""
        return f"TemplateString({self.template!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another TemplateString."""
        if isinstance(other, TemplateString):
            return self.template == other.template
        return False

    def __hash__(self) -> int:
        """Make TemplateString hashable."""
        return hash(self.template)

    # Duck typing methods to make it behave like a string for Pydantic validation
    def __len__(self) -> int:
        """Return length to behave like a string."""
        return len(self.template)

    def __contains__(self, item) -> bool:
        """Support 'in' operator to behave like a string."""
        return item in self.template

    def __getitem__(self, key):
        """Support indexing to behave like a string."""
        return self.template[key]

    def __iter__(self):
        """Support iteration to behave like a string."""
        return iter(self.template)

    # List-like methods for cases where template strings represent arrays
    def __getstate__(self):
        """Support pickling."""
        return {"template": self.template}

    def __setstate__(self, state):
        """Support unpickling."""
        self.template = state["template"]

    # Additional methods to help with Pydantic validation
    @classmethod
    def __get_validators__(cls):
        """Pydantic v1 compatibility."""
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        """Validate that the value is a string, TemplateString, or basic type."""
        if isinstance(v, cls):
            return v
        # Allow strings and basic types that can be converted to strings
        if isinstance(v, (str, int, float, bool)):
            return v
        # Allow Prompt objects (they have __str__ method and content attribute)
        if hasattr(v, "__str__") and hasattr(v, "content"):
            # This is likely a Prompt object
            return str(v)
        # Reject functions, lambdas, and other complex types
        if callable(v):
            raise ValueError(
                f"Template fields cannot accept callable objects like {type(v).__name__}"
            )
        # For other types, try to convert to string
        try:
            str(v)
            return v
        except Exception:
            raise ValueError(
                f"Template fields cannot accept objects of type {type(v).__name__}"
            )

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Pydantic v2 compatibility."""
        from pydantic_core import core_schema

        return core_schema.no_info_plain_validator_function(cls.validate)

    def to_template_string(self) -> str:
        """
        Convert back to the original template string format.

        This is used during the import process to convert the TemplateString
        object back to the raw template string.

        Returns:
            The original template string
        """
        return self.template
