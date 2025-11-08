"""
Browser automation helper for opening provider signup pages.

Handles cross-platform browser opening with graceful fallback to
manual URL navigation.
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



import webbrowser
from typing import Optional


class BrowserHelper:
    """
    Helper for opening provider API key pages in browser.

    Supports all major LLM providers with cross-platform compatibility.
    """

    # Provider API key URLs
    PROVIDER_URLS = {
        "anthropic": "https://console.anthropic.com/settings/keys",
        "openai": "https://platform.openai.com/api-keys",
        "gemini": "https://aistudio.google.com/app/apikey",
    }

    @staticmethod
    def open_provider_page(provider: str) -> tuple[bool, str]:
        """
        Open provider's API key page in browser.

        Args:
            provider: Provider name ("anthropic", "openai", "gemini")

        Returns:
            Tuple of (success: bool, url: str)
            - success: True if browser opened, False if failed
            - url: The URL (for manual fallback)
        """
        url = BrowserHelper.PROVIDER_URLS.get(provider)

        if not url:
            return False, ""

        try:
            # webbrowser.open() returns True if successful
            success = webbrowser.open(url)
            return success, url
        except Exception:
            # Browser opening failed, return URL for manual copy-paste
            return False, url

    @staticmethod
    def get_provider_url(provider: str) -> Optional[str]:
        """
        Get API key URL for a provider.

        Args:
            provider: Provider name

        Returns:
            URL string or None if provider unknown
        """
        return BrowserHelper.PROVIDER_URLS.get(provider)

    @staticmethod
    def get_instructions(provider: str) -> str:
        """
        Get provider-specific setup instructions.

        Args:
            provider: Provider name

        Returns:
            Multi-line instruction string
        """
        instructions = {
            "anthropic": (
                "1. Sign up or log in to Anthropic Console\n"
                "2. Navigate to 'API Keys' section\n"
                "3. Click 'Create Key'\n"
                "4. Copy your API key"
            ),
            "openai": (
                "1. Sign up or log in to OpenAI Platform\n"
                "2. Navigate to API keys page\n"
                "3. Click '+ Create new secret key'\n"
                "4. Give it a name and copy the key"
            ),
            "gemini": (
                "1. Sign up or log in to Google AI Studio\n"
                "2. Click 'Get API Key'\n"
                "3. Create a new API key or use existing\n"
                "4. Copy your API key"
            ),
        }
        return instructions.get(provider, "Follow provider instructions to get API key")
