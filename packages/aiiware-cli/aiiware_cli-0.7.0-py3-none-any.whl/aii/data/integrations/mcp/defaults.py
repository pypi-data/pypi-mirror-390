"""
Built-in Default MCP Server Configurations

Provides safe, zero-configuration defaults for MCP servers.
Users can override these by creating ~/.aii/mcp_servers.json

Default Servers:
- filesystem: Local file system access (limited to user's home directory)

Security:
- Only safe, read-write operations
- Limited to user's home directory by default
- No network access
- No credential requirements
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



from pathlib import Path
from typing import Dict, Any


def get_default_mcp_servers() -> Dict[str, Any]:
    """
    Get built-in default MCP server configurations.

    These servers are always available if no user configuration exists.
    They provide safe, universally useful functionality with zero setup.

    Returns:
        Dictionary in pure MCP standard format (compatible with Claude Desktop)
    """
    return {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    str(Path.home())
                ],
                "description": "Local filesystem access (read/write/search files in home directory)"
            }
        }
    }


# Metadata about default servers
DEFAULT_SERVER_METADATA = {
    "filesystem": {
        "enabled": True,
        "required_credentials": False,
        "network_access": False,
        "capabilities": ["read_file", "write_file", "list_files", "search_files"],
        "risk_level": "low",  # Safe operations, limited scope
        "description": "Access files in your home directory. Safe for reading project files, creating documents, etc."
    }
}


def get_server_description(server_name: str) -> str:
    """Get human-readable description of a server."""
    metadata = DEFAULT_SERVER_METADATA.get(server_name, {})
    return metadata.get("description", "No description available")


def is_server_safe(server_name: str) -> bool:
    """Check if a server is considered safe (low risk, no credentials)."""
    metadata = DEFAULT_SERVER_METADATA.get(server_name, {})
    return (
        metadata.get("risk_level") == "low" and
        not metadata.get("required_credentials", True)
    )
