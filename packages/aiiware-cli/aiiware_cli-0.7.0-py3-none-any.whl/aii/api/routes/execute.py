"""Function execution endpoint."""

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


from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from aii.api.models import ExecuteRequest, ExecuteResponse, ErrorResponse
from aii.api.middleware import verify_api_key, check_rate_limit, get_server_instance
from aii.api.formatters import format_completion_metadata
from aii.api.errors import (
    format_error_response,
    get_status_code,
    FunctionNotFoundError,
    FunctionExecutionError,
    AiiError,
)
from aii.core.models import RecognitionResult, RouteSource

router = APIRouter()


@router.post("/api/execute", response_model=ExecuteResponse, responses={
    400: {"model": ErrorResponse, "description": "Validation error"},
    401: {"model": ErrorResponse, "description": "Authentication error"},
    404: {"model": ErrorResponse, "description": "Function not found"},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
})
async def execute_function(
    http_request: Request,
    request: ExecuteRequest,
    api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Execute AII function with parameters.

    Example:
    ```bash
    curl -X POST http://localhost:16169/api/execute \\
      -H "Content-Type: application/json" \\
      -H "AII-API-Key: aii_sk_..." \\
      -d '{
        "function": "translate",
        "params": {"text": "hello", "target_language": "spanish"}
      }'
    ```

    Success Response:
    ```json
    {
      "success": true,
      "result": "hola",
      "metadata": {
        "tokens": {"input": 145, "output": 28},
        "cost": 0.0004,
        "execution_time": 1.23
      }
    }
    ```

    Error Response:
    ```json
    {
      "error": {
        "code": "FUNCTION_NOT_FOUND",
        "message": "Function 'invalid' not found",
        "details": {
          "function": "invalid",
          "available_functions": ["translate", "explain", ...]
        },
        "request_id": "req_abc123"
      }
    }
    ```
    """
    # Get request ID from middleware (RequestIDMiddleware)
    request_id = getattr(http_request.state, "request_id", None)

    server = get_server_instance()

    if not server:
        # Server not initialized - this is an internal error
        error_detail = format_error_response(
            Exception("Server not initialized"),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error=error_detail).dict()
        )

    try:
        # For API mode, use function name directly from request
        # API clients specify the function explicitly, no need for intent recognition
        function_name = request.function
        parameters = request.params or {}

        # Validate function exists - use structured error
        if function_name not in server.engine.function_registry.plugins:
            available = list(server.engine.function_registry.plugins.keys())
            raise FunctionNotFoundError(function_name, available)

        # Create recognition result for API execution
        recognition_result = RecognitionResult(
            intent=function_name,
            confidence=1.0,  # API clients explicitly specify function
            parameters=parameters,
            function_name=function_name,
            requires_confirmation=False,  # API execution doesn't require confirmation
            reasoning="Direct API invocation",
            source=RouteSource.DIRECT_MATCH
        )

        # Execute function via execution engine
        result = await server.engine.execution_engine.execute_function(
            recognition_result=recognition_result,
            user_input=request.get_formatted_input(),
            chat_context=None,
            config=server.engine.config,
            llm_provider=server.engine.llm_provider,
            web_client=server.engine.web_client,
            mcp_client=server.engine.mcp_client,
            offline_mode=False
        )

        return ExecuteResponse(
            success=result.success,
            result=result.data if result.success else None,
            error=result.message if not result.success else None,
            metadata=format_completion_metadata(result)
        )

    except AiiError as e:
        # Handle Aii-specific errors with structured response
        error_detail = format_error_response(e, request_id=request_id)
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(error=error_detail).dict()
        )

    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions (auth, rate limit, etc.)
        raise

    except Exception as e:
        # Handle unexpected errors with structured response
        error_detail = format_error_response(e, request_id=request_id)
        status_code = get_status_code(e)
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(error=error_detail).dict()
        )
