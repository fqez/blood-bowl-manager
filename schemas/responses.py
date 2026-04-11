"""Centralized API response helpers.

This module provides standardized response structures for all API endpoints.
"""

from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response model."""

    status_code: int
    response_type: str
    description: str
    data: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation completed successfully",
                "data": {"id": "example-id"},
            }
        }


def success_response(
    data: Any,
    description: str = "Operation completed successfully",
    status_code: int = 200,
) -> dict:
    """Create a standardized success response."""
    return {
        "status_code": status_code,
        "response_type": "success",
        "description": description,
        "data": data,
    }


def created_response(
    data: Any, description: str = "Resource created successfully"
) -> dict:
    """Create a standardized 201 created response."""
    return success_response(data, description, status_code=201)


def error_response(
    description: str = "An error occurred",
    status_code: int = 400,
    data: Any = None,
) -> dict:
    """Create a standardized error response."""
    return {
        "status_code": status_code,
        "response_type": "error",
        "description": description,
        "data": data,
    }


def not_found_response(resource: str, resource_id: str) -> dict:
    """Create a standardized 404 not found response."""
    return error_response(
        description=f"{resource} with ID: {resource_id} not found",
        status_code=404,
    )
