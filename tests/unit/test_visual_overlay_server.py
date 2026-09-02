"""Unit tests for VisualOverlayServer WebSocket bridge."""

import json

import pytest

from aria.core.pipeline.state import AssistantMode, PipelineState
from aria.visual.overlay.server import VisualOverlayServer
from aria.visual.overlay.state_machine import VisualStateMachine


class MockWebSocketClient:
    """Mock WebSocket client for testing broadcast."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, message: str) -> None:
        self.messages.append(message)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_visual_overlay_server_broadcast() -> None:
    vsm = VisualStateMachine(initial_mode=AssistantMode.ARIA)
    server = VisualOverlayServer(state_machine=vsm)

    client1 = MockWebSocketClient()
    client2 = MockWebSocketClient()

    server.register_client(client1)
    server.register_client(client2)
    assert server.client_count == 2

    # Broadcast a state snapshot
    snapshot = vsm.transition_state(PipelineState.LISTENING)
    await server.broadcast_snapshot(snapshot)

    assert len(client1.messages) == 1
    assert len(client2.messages) == 1

    payload = json.loads(client1.messages[0])
    assert payload["pipeline_state"] == "listening"
    assert payload["mode"] == "aria"

    # Unregister client
    server.unregister_client(client1)
    assert server.client_count == 1
