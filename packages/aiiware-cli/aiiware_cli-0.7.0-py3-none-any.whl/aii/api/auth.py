"""API key authentication for Aii API server."""

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


from aii.config.manager import ConfigManager


class APIKeyAuth:
    """API key authentication handler."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> set[str]:
        """Load API keys from config."""
        keys = self.config.get("api.keys", [])
        return set(keys)

    def verify_key(self, api_key: str) -> bool:
        """Verify API key is valid."""
        return api_key in self.api_keys

    def add_key(self, api_key: str):
        """Add new API key and persist to config."""
        self.api_keys.add(api_key)

        # Persist to config
        keys = list(self.api_keys)
        self.config.set("api.keys", keys)
