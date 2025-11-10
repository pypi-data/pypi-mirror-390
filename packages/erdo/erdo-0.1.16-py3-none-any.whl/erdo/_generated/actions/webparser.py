"""
Web parsing actions for extracting content from websites service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for webparser service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, Optional, Union

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


class ParseParams(BaseActionParams):
    """Parse website content using Jina's reader API to extract text, images, and links parameters"""

    name: str = "webparser.parse"  # Action type for roundtrip compatibility
    url: Optional[Union[str, TemplateString]] = None  # url parameter
    include_images: Optional[Union[bool, TemplateString]] = (
        None  # include_images parameter
    )
    include_links: Optional[Union[bool, TemplateString]] = (
        None  # include_links parameter
    )
    remove_selector: Optional[Union[str, TemplateString]] = (
        None  # remove_selector parameter
    )
    target_selector: Optional[Union[str, TemplateString]] = (
        None  # target_selector parameter
    )
    wait_for_selector: Optional[Union[str, TemplateString]] = (
        None  # wait_for_selector parameter
    )
    generate_image_alt: Optional[Union[bool, TemplateString]] = (
        None  # generate_image_alt parameter
    )
    return_format: Optional[Union[str, TemplateString]] = (
        None  # return_format parameter
    )
    timeout: Optional[Union[int, TemplateString]] = None  # timeout parameter
    no_cache: Optional[Union[bool, TemplateString]] = None  # no_cache parameter


class ParseResult(BaseModel):
    """Parse website content using Jina's reader API to extract text, images, and links result type

    Result schema for webparser.parse action.
    """

    content: str
    title: Optional[str]
    metadata: Optional[Any]


def parse(
    url: Optional[Union[str, TemplateString]] = None,
    include_images: Optional[Union[bool, TemplateString]] = None,
    include_links: Optional[Union[bool, TemplateString]] = None,
    remove_selector: Optional[Union[str, TemplateString]] = None,
    target_selector: Optional[Union[str, TemplateString]] = None,
    wait_for_selector: Optional[Union[str, TemplateString]] = None,
    generate_image_alt: Optional[Union[bool, TemplateString]] = None,
    return_format: Optional[Union[str, TemplateString]] = None,
    timeout: Optional[Union[int, TemplateString]] = None,
    no_cache: Optional[Union[bool, TemplateString]] = None,
    **params: Any,
) -> ParseParams:
    """Parse website content using Jina's reader API to extract text, images, and links

    Args:
        url: url parameter
        include_images: include_images parameter
        include_links: include_links parameter
        remove_selector: remove_selector parameter
        target_selector: target_selector parameter
        wait_for_selector: wait_for_selector parameter
        generate_image_alt: generate_image_alt parameter
        return_format: return_format parameter
        timeout: timeout parameter
        no_cache: no_cache parameter

    Returns:
        ParseParams: Type-safe parameter object
    """
    param_dict = {
        "url": url,
        "include_images": include_images,
        "include_links": include_links,
        "remove_selector": remove_selector,
        "target_selector": target_selector,
        "wait_for_selector": wait_for_selector,
        "generate_image_alt": generate_image_alt,
        "return_format": return_format,
        "timeout": timeout,
        "no_cache": no_cache,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = ParseParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
ParseParams._result = ParseResult
