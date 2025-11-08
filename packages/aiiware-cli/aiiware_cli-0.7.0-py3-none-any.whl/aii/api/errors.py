"""Structured error handling for Aii API.

Provides:
- Error code taxonomy
- Structured error responses
- Environment-aware traceback handling
- Type-safe error models
"""

# Copyright 2025-present aiiware.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import traceback
import logging
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """
    Error code taxonomy for Aii API.

    Format: CATEGORY_SPECIFIC_ERROR
    Categories: VALIDATION, AUTH, RATE_LIMIT, FUNCTION, LLM, MCP, INTERNAL
    """

    # Validation Errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    VALIDATION_MISSING_PARAMETER = "VALIDATION_MISSING_PARAMETER"
    VALIDATION_INVALID_PARAMETER = "VALIDATION_INVALID_PARAMETER"
    VALIDATION_INVALID_FUNCTION = "VALIDATION_INVALID_FUNCTION"

    # Authentication & Authorization Errors (401, 403)
    AUTH_MISSING_API_KEY = "AUTH_MISSING_API_KEY"
    AUTH_INVALID_API_KEY = "AUTH_INVALID_API_KEY"
    AUTH_DISABLED_API_KEY = "AUTH_DISABLED_API_KEY"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"

    # Rate Limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Function Execution Errors (400, 500)
    FUNCTION_NOT_FOUND = "FUNCTION_NOT_FOUND"
    FUNCTION_EXECUTION_FAILED = "FUNCTION_EXECUTION_FAILED"
    FUNCTION_PREREQUISITES_NOT_MET = "FUNCTION_PREREQUISITES_NOT_MET"
    FUNCTION_TIMEOUT = "FUNCTION_TIMEOUT"

    # LLM Provider Errors (500, 503)
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    LLM_PROVIDER_UNAVAILABLE = "LLM_PROVIDER_UNAVAILABLE"
    LLM_RATE_LIMIT_EXCEEDED = "LLM_RATE_LIMIT_EXCEEDED"
    LLM_CONTEXT_LENGTH_EXCEEDED = "LLM_CONTEXT_LENGTH_EXCEEDED"

    # MCP Integration Errors (500, 503)
    MCP_SERVER_ERROR = "MCP_SERVER_ERROR"
    MCP_SERVER_UNAVAILABLE = "MCP_SERVER_UNAVAILABLE"
    MCP_TOOL_NOT_FOUND = "MCP_TOOL_NOT_FOUND"
    MCP_TOOL_EXECUTION_FAILED = "MCP_TOOL_EXECUTION_FAILED"

    # Internal Server Errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INTERNAL_DATABASE_ERROR = "INTERNAL_DATABASE_ERROR"
    INTERNAL_CONFIGURATION_ERROR = "INTERNAL_CONFIGURATION_ERROR"


class ErrorDetail(BaseModel):
    """Structured error detail."""

    code: ErrorCode = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context-specific error details"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for debugging"
    )
    traceback: Optional[str] = Field(
        default=None,
        description="Stack trace (only in development mode)"
    )


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: ErrorDetail


class AiiError(Exception):
    """
    Base exception for Aii API errors.

    All Aii-specific errors should inherit from this class.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
        cause: Optional[Exception] = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.cause = cause
        super().__init__(message)

    def to_error_detail(
        self,
        request_id: Optional[str] = None,
        include_traceback: bool = False,
    ) -> ErrorDetail:
        """Convert to structured error detail."""
        error_detail = ErrorDetail(
            code=self.code,
            message=self.message,
            details=self.details,
            request_id=request_id,
        )

        if include_traceback and self.cause:
            error_detail.traceback = "".join(
                traceback.format_exception(
                    type(self.cause),
                    self.cause,
                    self.cause.__traceback__
                )
            )

        return error_detail


# Validation Errors (400)

class ValidationError(AiiError):
    """Validation error (missing or invalid parameters)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400,
        )


class MissingParameterError(AiiError):
    """Missing required parameter."""

    def __init__(self, parameter: str, function: Optional[str] = None):
        details = {"parameter": parameter}
        if function:
            details["function"] = function

        super().__init__(
            code=ErrorCode.VALIDATION_MISSING_PARAMETER,
            message=f"Missing required parameter: {parameter}",
            details=details,
            status_code=400,
        )


class InvalidParameterError(AiiError):
    """Invalid parameter value."""

    def __init__(
        self,
        parameter: str,
        value: Any,
        expected: str,
        function: Optional[str] = None,
    ):
        details = {
            "parameter": parameter,
            "value": str(value),
            "expected": expected,
        }
        if function:
            details["function"] = function

        super().__init__(
            code=ErrorCode.VALIDATION_INVALID_PARAMETER,
            message=f"Invalid value for parameter '{parameter}': expected {expected}",
            details=details,
            status_code=400,
        )


class FunctionNotFoundError(AiiError):
    """Function not found in registry."""

    def __init__(self, function_name: str, available_functions: Optional[list] = None):
        details = {"function": function_name}
        if available_functions:
            details["available_functions"] = available_functions[:10]  # Limit to 10

        super().__init__(
            code=ErrorCode.FUNCTION_NOT_FOUND,
            message=f"Function '{function_name}' not found",
            details=details,
            status_code=404,
        )


# Authentication Errors (401, 403)

class AuthenticationError(AiiError):
    """Authentication error."""

    def __init__(self, message: str, code: ErrorCode = ErrorCode.AUTH_INVALID_API_KEY):
        super().__init__(
            code=code,
            message=message,
            status_code=401,
        )


class MissingAPIKeyError(AuthenticationError):
    """Missing API key in request."""

    def __init__(self):
        super().__init__(
            message="API key required. Provide 'AII-API-Key' header.",
            code=ErrorCode.AUTH_MISSING_API_KEY,
        )


class InvalidAPIKeyError(AuthenticationError):
    """Invalid API key."""

    def __init__(self):
        super().__init__(
            message="Invalid API key",
            code=ErrorCode.AUTH_INVALID_API_KEY,
        )


class DisabledAPIKeyError(AiiError):
    """API key is disabled."""

    def __init__(self):
        super().__init__(
            code=ErrorCode.AUTH_DISABLED_API_KEY,
            message="API key has been disabled",
            status_code=403,
        )


# Rate Limiting (429)

class RateLimitError(AiiError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            details=details,
            status_code=429,
        )


# Function Execution Errors (400, 500)

class FunctionExecutionError(AiiError):
    """Function execution failed."""

    def __init__(
        self,
        function_name: str,
        message: str,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            code=ErrorCode.FUNCTION_EXECUTION_FAILED,
            message=f"Function '{function_name}' execution failed: {message}",
            details={"function": function_name},
            status_code=500,
            cause=cause,
        )


class FunctionPrerequisitesError(AiiError):
    """Function prerequisites not met."""

    def __init__(self, function_name: str, missing: list):
        super().__init__(
            code=ErrorCode.FUNCTION_PREREQUISITES_NOT_MET,
            message=f"Function '{function_name}' prerequisites not met",
            details={
                "function": function_name,
                "missing_prerequisites": missing,
            },
            status_code=400,
        )


# LLM Provider Errors (500, 503)

class LLMProviderError(AiiError):
    """LLM provider error."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if provider:
            details["provider"] = provider

        super().__init__(
            code=ErrorCode.LLM_PROVIDER_ERROR,
            message=f"LLM provider error: {message}",
            details=details,
            status_code=500,
            cause=cause,
        )


class LLMProviderUnavailableError(AiiError):
    """LLM provider unavailable."""

    def __init__(self, provider: Optional[str] = None):
        details = {}
        if provider:
            details["provider"] = provider

        super().__init__(
            code=ErrorCode.LLM_PROVIDER_UNAVAILABLE,
            message="LLM provider is currently unavailable",
            details=details,
            status_code=503,
        )


# MCP Integration Errors (500, 503)

class MCPServerError(AiiError):
    """MCP server error."""

    def __init__(
        self,
        server_name: str,
        message: str,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            code=ErrorCode.MCP_SERVER_ERROR,
            message=f"MCP server '{server_name}' error: {message}",
            details={"server": server_name},
            status_code=500,
            cause=cause,
        )


# Utility Functions

def is_development_mode() -> bool:
    """
    Check if running in development mode.

    Development mode is enabled if:
    - AII_DEBUG environment variable is set to '1' or 'true'
    - AII_ENV environment variable is set to 'development'
    """
    debug = os.getenv("AII_DEBUG", "").lower() in ("1", "true")
    env = os.getenv("AII_ENV", "production").lower()
    return debug or env == "development"


def format_error_response(
    error: Exception,
    request_id: Optional[str] = None,
) -> ErrorDetail:
    """
    Format any exception as structured error response.

    Args:
        error: Exception to format
        request_id: Optional request ID for tracing

    Returns:
        ErrorDetail with appropriate error code and message
    """
    include_traceback = is_development_mode()

    # Handle Aii-specific errors
    if isinstance(error, AiiError):
        error_detail = error.to_error_detail(
            request_id=request_id,
            include_traceback=include_traceback,
        )

        # Log error with context
        logger.error(
            f"Aii error: {error.code.value}",
            extra={
                "error_code": error.code.value,
                "message": error.message,
                "details": error.details,
                "request_id": request_id,
            },
            exc_info=error.cause if include_traceback else None,
        )

        return error_detail

    # Handle generic exceptions
    error_detail = ErrorDetail(
        code=ErrorCode.INTERNAL_ERROR,
        message="Internal server error" if not include_traceback else str(error),
        request_id=request_id,
    )

    if include_traceback:
        error_detail.traceback = traceback.format_exc()

    # Log unexpected errors
    logger.exception(
        "Unexpected error",
        extra={
            "error_type": type(error).__name__,
            "message": str(error),
            "request_id": request_id,
        },
    )

    return error_detail


def get_status_code(error: Exception) -> int:
    """Get HTTP status code for exception."""
    if isinstance(error, AiiError):
        return error.status_code
    return 500  # Default to 500 for unknown errors
