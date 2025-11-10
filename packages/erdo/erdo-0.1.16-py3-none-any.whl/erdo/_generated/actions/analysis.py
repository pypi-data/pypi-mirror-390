"""
Analysis actions for creating and managing data analysis service functions.
Auto-generated - DO NOT EDIT.

Provides type-safe action definitions for analysis service.
Actual execution happens in the Go backend after syncing.
"""

from typing import Any, List, Optional, Union

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


class CreateAnalysisParams(BaseActionParams):
    """Create an analysis for a dataset, resource, or dataset-resource combination parameters"""

    name: str = "analysis.create_analysis"  # Action type for roundtrip compatibility
    analysis: Optional[Any] = None  # analysis parameter
    dataset_slug: Optional[Union[str, TemplateString]] = None  # dataset_slug parameter
    resource_id: Optional[Union[str, TemplateString]] = None  # resource_id parameter


class AnalyzeCsvParams(BaseActionParams):
    """Analyze CSV file using Go-based CSV analyzer (fast, no Python needed) parameters"""

    name: str = "analysis.analyze_csv"  # Action type for roundtrip compatibility
    file: Optional[Any] = None  # file parameter
    columns: Optional[Any] = None  # columns parameter
    rows: Optional[Any] = None  # rows parameter
    encryption_key: Optional[Union[str, TemplateString]] = (
        None  # encryption_key parameter
    )


class AnalyzeExcelParams(BaseActionParams):
    """Analyze Excel file using Go-based Excel analyzer (fast, no Python needed) parameters"""

    name: str = "analysis.analyze_excel"  # Action type for roundtrip compatibility
    file: Optional[Any] = None  # file parameter
    encryption_key: Optional[Union[str, TemplateString]] = (
        None  # encryption_key parameter
    )


class CreateAnalysisResult(BaseModel):
    """Create an analysis for a dataset, resource, or dataset-resource combination result type

    Result schema for analysis.create_analysis action.
    """

    analysis: Any
    insights: Optional[List[str]]
    recommendations: Optional[List[str]]


class AnalyzeCsvResult(BaseModel):
    """Analyze CSV file using Go-based CSV analyzer (fast, no Python needed) result type

    Result schema for analysis.analyze_csv action.
    """

    summary: str
    details: Any
    dataset_file_name: str


class AnalyzeExcelResult(BaseModel):
    """Analyze Excel file using Go-based Excel analyzer (fast, no Python needed) result type

    Result schema for analysis.analyze_excel action.
    """

    summary: str
    details: Any
    dataset_file_name: str


def create_analysis(
    analysis: Optional[Any] = None,
    dataset_slug: Optional[Union[str, TemplateString]] = None,
    resource_id: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> CreateAnalysisParams:
    """Create an analysis for a dataset, resource, or dataset-resource combination

    Args:
        analysis: analysis parameter
        dataset_slug: dataset_slug parameter
        resource_id: resource_id parameter

    Returns:
        CreateAnalysisParams: Type-safe parameter object
    """
    param_dict = {
        "analysis": analysis,
        "dataset_slug": dataset_slug,
        "resource_id": resource_id,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = CreateAnalysisParams(**param_dict)
    return params_obj


def analyze_csv(
    file: Optional[Any] = None,
    columns: Optional[Any] = None,
    rows: Optional[Any] = None,
    encryption_key: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> AnalyzeCsvParams:
    """Analyze CSV file using Go-based CSV analyzer (fast, no Python needed)

    Args:
        file: file parameter
        columns: columns parameter
        rows: rows parameter
        encryption_key: encryption_key parameter

    Returns:
        AnalyzeCsvParams: Type-safe parameter object
    """
    param_dict = {
        "file": file,
        "columns": columns,
        "rows": rows,
        "encryption_key": encryption_key,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = AnalyzeCsvParams(**param_dict)
    return params_obj


def analyze_excel(
    file: Optional[Any] = None,
    encryption_key: Optional[Union[str, TemplateString]] = None,
    **params: Any,
) -> AnalyzeExcelParams:
    """Analyze Excel file using Go-based Excel analyzer (fast, no Python needed)

    Args:
        file: file parameter
        encryption_key: encryption_key parameter

    Returns:
        AnalyzeExcelParams: Type-safe parameter object
    """
    param_dict = {
        "file": file,
        "encryption_key": encryption_key,
    }
    # Remove None values for optional parameters
    param_dict = {k: v for k, v in param_dict.items() if v is not None}
    param_dict.update(params)
    params_obj = AnalyzeExcelParams(**param_dict)
    return params_obj


# Associate parameter classes with their result types
CreateAnalysisParams._result = CreateAnalysisResult
AnalyzeCsvParams._result = AnalyzeCsvResult
AnalyzeExcelParams._result = AnalyzeExcelResult
