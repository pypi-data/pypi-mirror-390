"""Git Functions - Git workflow automation with AI assistance

NOTE: This file now contains only stateless git functions that don't require file system access.
Legacy server-side git operation functions (GitCommitFunction, GitPRFunction, GitBranchFunction)
have been removed in v0.6.0 as part of the unified architecture refactoring.

Use Client-Owned Workflows instead:
- For git commit: `aii run git commit` (not `aii commit`)
- For pull requests: `aii run git pr` (not `aii pr`)
- For branches: Use git CLI directly

See: system-dev-docs/aii-cli/issues/issue-005-v0.6.0-architecture-compliance-audit.md
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



import subprocess
from typing import Any

from ...core.models import (
    ExecutionContext,
    ExecutionResult,
    FunctionCategory,
    FunctionPlugin,
    FunctionSafety,
    ParameterSchema,
    ValidationResult,
)

# Import individual function implementations
from .git_diff import GitDiffFunction
from .git_status import GitStatusFunction