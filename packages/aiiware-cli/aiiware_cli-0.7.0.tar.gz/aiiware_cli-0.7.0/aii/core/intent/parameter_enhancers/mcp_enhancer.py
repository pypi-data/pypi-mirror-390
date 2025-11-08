"""Parameter enhancer for MCP functions."""

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


from typing import Any

from .base_enhancer import BaseEnhancer


class MCPEnhancer(BaseEnhancer):
    """Enhancer for mcp_tool function."""

    @property
    def supported_functions(self) -> list[str]:
        return ["mcp_tool"]

    def enhance(
        self, parameters: dict, user_input: str, context: Any = None
    ) -> dict:
        """Enhance MCP tool parameters.

        MCP tool function expects a 'user_request' parameter containing the full
        natural language request. The function will then use LLM to select the
        appropriate MCP tool and generate arguments.
        """
        # Always provide the full user input as user_request
        parameters["user_request"] = user_input

        self.debug(f"Enhanced mcp_tool parameters: {parameters}")
        return parameters
