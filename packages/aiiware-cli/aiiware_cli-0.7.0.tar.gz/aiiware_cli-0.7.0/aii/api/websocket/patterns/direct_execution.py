"""Direct execution pattern - Direct function invocation."""

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


from typing import Dict, Any
from fastapi import WebSocket

from aii.core.models import RecognitionResult, RouteSource


async def handle_direct_execution_pattern(
    websocket: WebSocket,
    data: Dict[str, Any],
    server: Any
) -> RecognitionResult:
    """
    Handle direct execution pattern (domain operations or legacy format).

    Pattern 2: Client specifies exact function + parameters.

    Args:
        websocket: FastAPI WebSocket connection
        data: Request data containing function and params
        server: APIServer instance

    Returns:
        RecognitionResult for direct invocation

    Raises:
        Exception: If function not found
    """
    function_name = data.get("function", "")
    parameters = data.get("params", {})

    # Validate function exists first
    if function_name not in server.engine.function_registry.plugins:
        await websocket.send_json({
            "type": "error",
            "message": f"Function '{function_name}' not found"
        })
        raise ValueError(f"Function '{function_name}' not found")

    # Create recognition result for direct invocation
    recognition_result = RecognitionResult(
        intent=function_name,
        confidence=1.0,
        parameters=parameters,
        function_name=function_name,
        requires_confirmation=False,
        reasoning="Direct WebSocket invocation",
        source=RouteSource.DIRECT_MATCH
    )

    return recognition_result
