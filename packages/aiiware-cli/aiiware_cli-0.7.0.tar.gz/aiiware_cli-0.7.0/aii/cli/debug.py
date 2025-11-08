"""
Debug logging utility for AII CLI.

Enable debug output by setting environment variable:
    AII_DEBUG=1 aii "your command"
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
import sys


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled via AII_DEBUG environment variable."""
    return os.environ.get("AII_DEBUG", "0") == "1"


def debug_print(message: str, flush: bool = True) -> None:
    """
    Print debug message only if AII_DEBUG=1.

    Args:
        message: Debug message to print
        flush: Whether to flush stdout immediately (default: True)
    """
    if is_debug_enabled():
        print(f"[DEBUG] {message}", file=sys.stderr, flush=flush)
