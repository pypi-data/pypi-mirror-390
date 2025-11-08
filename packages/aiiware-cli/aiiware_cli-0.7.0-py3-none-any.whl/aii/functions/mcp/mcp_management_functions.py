"""
MCP Server Management Functions

Commands for managing MCP server configurations:
- mcp_add: Add a new MCP server
- mcp_remove: Remove an MCP server
- mcp_list: List all configured servers
- mcp_enable: Enable a disabled server
- mcp_disable: Disable a server (keeps config)
- mcp_catalog: List popular pre-configured servers
- mcp_install: Install server from catalog
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



import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ...core.models import (
    ExecutionContext,
    ExecutionResult,
    FunctionCategory,
    FunctionPlugin,
    FunctionSafety,
    OutputMode,
    ParameterSchema,
)
from .config_manager import MCPConfigManager

logger = logging.getLogger(__name__)


from .mcp_add import MCPAddFunction
from .mcp_remove import MCPRemoveFunction
from .mcp_list import MCPListFunction

from .mcp_enable import MCPEnableFunction
from .mcp_disable import MCPDisableFunction
from .mcp_catalog import MCPCatalogFunction

from .mcp_install import MCPInstallFunction
from .mcp_status import MCPStatusFunction

from .mcp_test import MCPTestFunction
from .mcp_update import MCPUpdateFunction

# Import GitHub function (moved to github/ module)
from ..github import GitHubIssueFunction

