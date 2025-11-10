"""
PDF extraction actions for extracting tables and text from PDF documents using Document AI and Gemini service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for pdfextractor service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from erdo.template import TemplateString
from erdo.types import StepMetadata


class ExtractParams(BaseModel):
    """Extract tables and text from PDF documents using Google Document AI with Gemini fallback parameters"""

    name: str = "pdfextractor.extract"  # Action type for roundtrip compatibility
    file_path: Optional[Union[str, TemplateString]] = None  # file_path parameter
    url: Optional[Union[str, TemplateString]] = None  # url parameter
    dataset_id: Optional[Union[str, TemplateString]] = None  # dataset_id parameter
    content: Optional[Union[str, TemplateString]] = None  # content parameter
    extract_tables: Optional[Union[bool, TemplateString]] = (
        None  # extract_tables parameter
    )
    extract_text: Optional[Union[bool, TemplateString]] = None  # extract_text parameter
    fallback_to_gemini: Optional[Union[bool, TemplateString]] = (
        None  # fallback_to_gemini parameter
    )
    timeout_seconds: Optional[Union[int, TemplateString]] = (
        None  # timeout_seconds parameter
    )


class ExtractResult(BaseModel):
    """Extract tables and text from PDF documents using Google Document AI with Gemini fallback result type

    Result schema for pdfextractor.extract action.
    """

    tables: List[Dict[str, Any]]
    page_count: float
    extraction_method: str
    processing_time_ms: float
    file_size_bytes: float
    text: Optional[str]
    warnings: Optional[List[str]]


def extract(
    file_path: Optional[Union[str, TemplateString]] = None,
    url: Optional[Union[str, TemplateString]] = None,
    dataset_id: Optional[Union[str, TemplateString]] = None,
    content: Optional[Union[str, TemplateString]] = None,
    extract_tables: Optional[Union[bool, TemplateString]] = None,
    extract_text: Optional[Union[bool, TemplateString]] = None,
    fallback_to_gemini: Optional[Union[bool, TemplateString]] = None,
    timeout_seconds: Optional[Union[int, TemplateString]] = None,
    step_metadata: Optional[StepMetadata] = None,
    **params: Any,
) -> ExtractParams:
    """Extract tables and text from PDF documents using Google Document AI with Gemini fallback

    Args:
        file_path: file_path parameter
        url: url parameter
        dataset_id: dataset_id parameter
        content: content parameter
        extract_tables: extract_tables parameter
        extract_text: extract_text parameter
        fallback_to_gemini: fallback_to_gemini parameter
        timeout_seconds: timeout_seconds parameter

    Returns:
        ExtractParams: Type-safe parameter object
    """
    param_dict = {
        "file_path": file_path,
        "url": url,
        "dataset_id": dataset_id,
        "content": content,
        "extract_tables": extract_tables,
        "extract_text": extract_text,
        "fallback_to_gemini": fallback_to_gemini,
        "timeout_seconds": timeout_seconds,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)

    return ExtractParams(**param_dict)


# Associate parameter classes with their result types
ExtractParams._result = ExtractResult
