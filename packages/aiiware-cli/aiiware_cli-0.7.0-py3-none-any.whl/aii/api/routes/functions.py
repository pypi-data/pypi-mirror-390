"""Functions listing endpoint."""

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


from fastapi import APIRouter, HTTPException, Depends

from aii.api.models import FunctionsResponse, FunctionInfo
from aii.api.middleware import verify_api_key, check_rate_limit, get_server_instance

router = APIRouter()


@router.get("/api/functions", response_model=FunctionsResponse)
async def list_functions(
    api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    List all available AII functions.

    Response:
    ```json
    {
      "functions": [
        {
          "name": "translate",
          "description": "Translate text to another language",
          "parameters": {...},
          "safety": "safe",
          "default_output_mode": "clean"
        }
      ]
    }
    ```
    """
    server = get_server_instance()

    if not server:
        raise HTTPException(status_code=500, detail="Server not initialized")

    # Get all registered plugins
    plugins = server.engine.function_registry.plugins.values()

    functions_list = []
    for f in plugins:
        # Handle different attribute names (function_name vs name)
        name = getattr(f, 'function_name', None) or getattr(f, 'name', 'unknown')
        description = getattr(f, 'function_description', None) or getattr(f, 'description', '')

        # Get default output mode safely
        default_mode = None
        if hasattr(f, 'default_output_mode'):
            mode_attr = getattr(f, 'default_output_mode', None)
            if mode_attr and hasattr(mode_attr, 'value'):
                default_mode = mode_attr.value

        functions_list.append(FunctionInfo(
            name=name,
            description=description,
            parameters=f.get_parameters_schema() if hasattr(f, 'get_parameters_schema') else {},
            safety=f.get_function_safety().value if hasattr(f, 'get_function_safety') else 'unknown',
            default_output_mode=default_mode
        ))

    return FunctionsResponse(functions=functions_list)
