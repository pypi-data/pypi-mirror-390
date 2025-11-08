"""Streaming utilities for WebSocket token delivery."""

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


from typing import Callable
from fastapi import WebSocket


def create_streaming_callback(websocket: WebSocket) -> Callable[[str], None]:
    """
    Create streaming callback for real-time token delivery.

    Args:
        websocket: FastAPI WebSocket connection

    Returns:
        Async callback function that sends tokens to client
    """
    async def streaming_callback(token: str):
        """Send each token immediately to the client"""
        try:
            await websocket.send_json({
                "type": "token",
                "data": token
            })
        except Exception as e:
            # WebSocket may have disconnected
            print(f"Failed to send token via WebSocket: {e}")

    return streaming_callback
