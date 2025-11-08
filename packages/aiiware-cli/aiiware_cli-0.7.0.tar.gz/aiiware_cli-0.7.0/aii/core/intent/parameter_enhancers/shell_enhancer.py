"""Parameter enhancer for shell functions."""

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


class ShellEnhancer(BaseEnhancer):
    """Enhancer for shell command functions."""

    @property
    def supported_functions(self) -> list[str]:
        return [
            "shell_command",
            "streaming_shell",
            "contextual_shell",
            "enhanced_shell",
        ]

    def enhance(
        self, parameters: dict, user_input: str, context: Any = None
    ) -> dict:
        """Enhance shell command parameters.

        Shell functions typically receive parameters normalized by the recognizer.
        This enhancer ensures parameter name consistency.
        """
        # Normalize parameter names (command → request)
        parameters = self.normalize_parameter(parameters, "command", "request")

        # Ensure request exists
        if "request" not in parameters:
            parameters["request"] = user_input.strip()

        # Default execute to True (with confirmation)
        if "execute" not in parameters:
            parameters["execute"] = True

        self.debug(f"Enhanced shell parameters: {parameters}")
        return parameters
