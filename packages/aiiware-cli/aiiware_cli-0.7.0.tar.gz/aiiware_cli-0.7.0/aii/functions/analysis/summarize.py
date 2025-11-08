"""Summarize Function - Summarize documents, articles, or content."""

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
from typing import Any

from ...cli.status_display import ProgressTracker
from ...core.models import (
    ExecutionContext,
    ExecutionResult,
    FunctionCategory,
    FunctionPlugin,
    FunctionSafety,
    OutputMode,
    ParameterSchema,
    ValidationResult,
)


class SummarizeFunction(FunctionPlugin):
    """Summarize documents, articles, or content"""

    @property
    def name(self) -> str:
        return "summarize"

    @property
    def description(self) -> str:
        return "Summarize documents, articles, or text content"

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.ANALYSIS

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "content": ParameterSchema(
                name="content",
                type="string",
                required=False,
                description="Text content to summarize (if not using file_path)",
            ),
            "file_path": ParameterSchema(
                name="file_path",
                type="string",
                required=False,
                description="Path to file to summarize (if not using content)",
            ),
            "length": ParameterSchema(
                name="length",
                type="string",
                required=False,
                description="Summary length",
                choices=["brief", "medium", "detailed"],
                default="medium",
            ),
            "format": ParameterSchema(
                name="format",
                type="string",
                required=False,
                description="Summary format",
                choices=["paragraph", "bullet_points", "structured"],
                default="structured",
            ),
            "language": ParameterSchema(
                name="language",
                type="string",
                required=False,
                description="Output language for the summary (e.g., 'chinese', 'english', 'spanish')",
                choices=["chinese", "english", "spanish", "french", "german", "japanese", "korean", "italian", "portuguese"],
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        """Summarize should show clean output by default (just the summary)"""
        return OutputMode.CLEAN

    @property
    def supports_output_modes(self) -> list[OutputMode]:
        """Summarize supports all output modes"""
        return [OutputMode.CLEAN, OutputMode.STANDARD, OutputMode.THINKING]

    async def validate_prerequisites(
        self, context: ExecutionContext
    ) -> ValidationResult:
        """Check prerequisites"""
        content = context.parameters.get("content")
        file_path = context.parameters.get("file_path")

        if not content and not file_path:
            return ValidationResult(
                valid=False,
                errors=["Either content or file_path must be provided"],
            )

        if file_path:
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    valid=False, errors=[f"File not found: {file_path}"]
                )

            # Check file size (max 500KB)
            if path.stat().st_size > 500 * 1024:
                return ValidationResult(
                    valid=False,
                    errors=["File too large for summarization (max 500KB)"],
                )

        if not context.llm_provider:
            return ValidationResult(
                valid=False,
                errors=["LLM provider required for summarization"],
            )

        return ValidationResult(valid=True)

    async def execute(
        self, parameters: dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """Execute summarization"""
        content = parameters.get("content")
        file_path = parameters.get("file_path")
        length = parameters.get("length", "medium")
        format_type = parameters.get("format", "structured")

        try:
            # Get content
            if file_path and not content:
                path = Path(file_path)
                content = path.read_text(encoding="utf-8")
                source = f"file: {file_path}"
            else:
                source = "provided text"

            if not content:
                return ExecutionResult(success=False, message="No content to summarize")

            # Extract language parameter for language-specific summaries
            language = parameters.get("language")

            summary, usage = await self._generate_summary(
                content, length, format_type, context.llm_provider, language
            )

            # Create reasoning for THINKING mode
            reasoning_parts = [f"Summarizing content from {source}"]
            reasoning_parts.append(f"generating {length} summary in {format_type} format")
            if language:
                reasoning_parts.append(f"outputting in {language}")
            reasoning = ", ".join(reasoning_parts) + "."

            return ExecutionResult(
                success=True,
                message=f"# Summary ({source})\n\n{summary}",
                data={
                    "clean_output": summary,  # For CLEAN mode
                    "summary": summary,
                    "source": source,
                    "length": length,
                    "reasoning": reasoning,  # For THINKING/VERBOSE modes
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "reasoning_tokens": usage.get("reasoning_tokens", 0),
                    "format": format_type,
                    "original_length": len(content),
                },
            )

        except Exception as e:
            return ExecutionResult(
                success=False, message=f"Summarization failed: {str(e)}"
            )

    async def _generate_summary(
        self, content: str, length: str, format_type: str, llm_provider: Any, language: str = None
    ) -> str:
        """Generate summary using LLM"""
        length_instructions = {
            "brief": "Create a very concise summary (2-3 sentences)",
            "medium": "Create a balanced summary (1-2 paragraphs)",
            "detailed": "Create a comprehensive summary with key details",
        }

        format_instructions = {
            "paragraph": "Format as flowing paragraphs",
            "bullet_points": "Format as bullet points",
            "structured": "Use structured format with headers and bullet points",
        }

        length_instruction = length_instructions.get(
            length, length_instructions["medium"]
        )
        format_instruction = format_instructions.get(
            format_type, format_instructions["structured"]
        )

        # Truncate content if too long for LLM
        if len(content) > 8000:
            content = content[:8000] + "..."

        # Add language instruction if specified
        language_instruction = ""
        if language:
            language_map = {
                "chinese": "中文 (Chinese)",
                "english": "English",
                "spanish": "Spanish",
                "french": "French",
                "german": "German",
                "japanese": "Japanese",
                "korean": "Korean",
                "italian": "Italian",
                "portuguese": "Portuguese",
            }
            language_name = language_map.get(language.lower(), language)
            language_instruction = f"**CRITICAL REQUIREMENT**: Write the ENTIRE summary in {language_name} ONLY. Do not use English at all"

        # Build requirements list
        requirements = [
            length_instruction,
            format_instruction,
            "Focus on the most important points and key takeaways",
            "Maintain accuracy and don't add information not in the original",
            "Use clear, concise language",
            "If structured format, use markdown headers and bullet points"
        ]

        # Add language instruction if specified
        if language_instruction:
            requirements.insert(0, language_instruction)  # Put language first for emphasis

        requirements_text = "\n".join(f"- {req}" for req in requirements)

        # Special handling for language-specific summaries
        if language:
            prompt = f"""IMPORTANT: You must write the summary in {language_map.get(language.lower(), language)} ONLY. Do not use English.

Summarize the following content in {language_map.get(language.lower(), language)}:

{content}

Requirements:
{requirements_text}

Generate the summary in {language_map.get(language.lower(), language)}:"""
        else:
            prompt = f"""Summarize the following content:

{content}

Requirements:
{requirements_text}

Generate the summary:"""

        try:
            # Get streaming callback if available
            streaming_callback = getattr(llm_provider, '_streaming_callback', None)

            # Use complete_with_usage to track token consumption
            if hasattr(llm_provider, "complete_with_usage"):
                llm_response = await llm_provider.complete_with_usage(
                    prompt,
                    on_token=streaming_callback
                )
                result = llm_response.content
                usage = llm_response.usage or {}
            else:
                result = await llm_provider.complete(prompt)
                usage = {}

            return (
                str(result) if result is not None else "Failed to generate summary",
                usage
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {str(e)}") from e


