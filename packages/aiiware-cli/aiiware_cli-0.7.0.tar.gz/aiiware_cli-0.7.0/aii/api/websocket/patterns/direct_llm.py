"""Direct LLM call pattern - Prompt library natural language mode."""

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


from typing import Dict, Any
from fastapi import WebSocket
import time

from aii.core.models import ExecutionResult
from aii.api.utils import is_debug_enabled


async def handle_direct_llm_pattern(
    websocket: WebSocket,
    data: Dict[str, Any],
    server: Any,
    streaming_callback
) -> ExecutionResult:
    """
    Handle direct LLM call pattern (v0.6.1 Prompt Library natural_language mode).

    Pattern 3: Client provides custom system_prompt + user_prompt, server calls LLM directly.
    Bypasses intent recognition and uses ONLY the custom system prompt.

    Args:
        websocket: FastAPI WebSocket connection
        data: Request data containing system_prompt, user_prompt, prompt_name
        server: APIServer instance
        streaming_callback: Async callback for token streaming

    Returns:
        ExecutionResult with LLM response

    Raises:
        Exception: If LLM call fails
    """
    system_prompt = data.get("system_prompt")
    user_prompt = data.get("user_prompt")
    prompt_name = data.get("prompt_name")

    # v0.6.2: Call LLM directly with ONLY the custom system_prompt + user_input
    # Do NOT use universal_generate (which adds orchestrator prompts)
    try:
        # Assemble full prompt (system_prompt + user_input in triple quotes)
        # v0.6.2: Wrap user input in triple quotes for better prompt adherence
        assembled_prompt = f"{system_prompt}\n\n\"\"\"{user_prompt}\"\"\""

        # Get display name
        display_name = prompt_name if prompt_name else "direct_llm_call"

        # Call LLM provider directly (bypass universal_generate orchestrator)
        start_time = time.time()

        llm_response = await server.engine.llm_provider.complete_with_usage(
            prompt=assembled_prompt,
            on_token=streaming_callback  # Fixed: use on_token parameter
        )

        execution_time = time.time() - start_time

        # Build ExecutionResult from LLM response
        result = ExecutionResult(
            success=True,
            message=llm_response.content,
            function_name=display_name,
            data={
                "content": llm_response.content,
                "clean_output": llm_response.content,
                "input_tokens": llm_response.usage.get("input_tokens", 0) if llm_response.usage else 0,
                "output_tokens": llm_response.usage.get("output_tokens", 0) if llm_response.usage else 0,
                "cost": llm_response.usage.get("cost", 0) if llm_response.usage else 0,
                "model": llm_response.model,
                "reasoning": f"Direct LLM call with custom prompt: {display_name}",
                "generation_method": "direct_llm_call",
                "original_request": user_prompt,
                "prompt_name": prompt_name,
            },
            execution_time=execution_time
        )

        # v0.6.2: Calculate cost using CostCalculator (direct LLM call bypasses ExecutionEngine)
        if server.engine.execution_engine.cost_calculator:
            try:
                provider_name = getattr(server.engine.llm_provider, 'provider_name', 'unknown')
                model_name = getattr(server.engine.llm_provider, 'model_name', 'unknown')

                cost_breakdown = server.engine.execution_engine.cost_calculator.calculate_cost(
                    provider=provider_name,
                    model=model_name,
                    input_tokens=result.data.get('input_tokens', 0),
                    output_tokens=result.data.get('output_tokens', 0),
                    reasoning_tokens=0
                )
                result.data['cost'] = cost_breakdown.total_cost
            except Exception as e:
                # Silently fail on cost calculation (non-critical feature)
                result.data['cost'] = 0.0

        return result

    except Exception as e:
        if is_debug_enabled():
            import traceback
            traceback.print_exc()
        await websocket.send_json({
            "type": "error",
            "message": f"Direct LLM call failed: {str(e)}"
        })
        # Don't close here - let main handler clean up
        raise
