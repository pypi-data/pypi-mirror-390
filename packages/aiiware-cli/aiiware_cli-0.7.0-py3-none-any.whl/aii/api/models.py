"""Pydantic models for API requests and responses."""

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



from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# Export error models for use in routes
from .errors import ErrorResponse, ErrorDetail, ErrorCode


class ExecuteRequest(BaseModel):
    """Request to execute AII function."""

    function: str = Field(..., description="Function name to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Function parameters")
    streaming: bool = Field(default=False, description="Enable streaming response")

    def get_formatted_input(self) -> str:
        """
        Format as natural language input for engine.

        The engine will recognize the function and parameters through
        its LLM-first intent recognition system.
        """
        if not self.params:
            return self.function

        # Format parameters as key=value pairs
        param_str = " ".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.function} {param_str}"


class ExecuteResponse(BaseModel):
    """Response from function execution."""

    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FunctionInfo(BaseModel):
    """Function metadata."""

    name: str
    description: str
    parameters: Dict[str, Any]
    safety: str
    default_output_mode: Optional[str] = None


class FunctionsResponse(BaseModel):
    """List of available functions."""

    functions: List[FunctionInfo]


class StatusResponse(BaseModel):
    """Server health status."""

    status: str
    version: str
    uptime: float
    mcp_servers: Optional[Dict[str, int]] = None
    initialization: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Initialization status for LLM provider and integrations"
    )


class MCPStatusRequest(BaseModel):
    """Request MCP server status."""

    server_name: Optional[str] = Field(
        default=None,
        description="Specific server name (null for all servers)"
    )
