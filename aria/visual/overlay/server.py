"""WebSocket streaming server bridging VisualStateMachine to overlay frontends."""

import asyncio
import json
import logging
from dataclasses import asdict
from typing import Any

from aria.visual.overlay.state_machine import VisualStateMachine, VisualStateSnapshot

logger = logging.getLogger(__name__)


class VisualOverlayServer:
    """Streams visual state snapshots over WebSocket to connected overlay clients."""

    def __init__(
        self,
        state_machine: VisualStateMachine,
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        self.state_machine = state_machine
        self.host = host
        self.port = port
        self._connected_clients: set[Any] = set()
        self._is_running = False

    def get_snapshot_payload(self, snapshot: VisualStateSnapshot) -> str:
        """Serialize snapshot to JSON."""
        data: dict[str, Any] = asdict(snapshot)
        data["pipeline_state"] = snapshot.pipeline_state.value
        data["mode"] = snapshot.mode.value
        data["timestamp"] = snapshot.timestamp.isoformat()
        return json.dumps(data)

    async def broadcast_snapshot(self, snapshot: VisualStateSnapshot) -> None:
        """Broadcast updated snapshot to all connected overlay windows."""
        if not self._connected_clients:
            return

        payload = self.get_snapshot_payload(snapshot)
        tasks = []
        for client in list(self._connected_clients):
            tasks.append(client.send(payload))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def register_client(self, client: Any) -> None:
        """Register a connected overlay websocket client."""
        self._connected_clients.add(client)

    def unregister_client(self, client: Any) -> None:
        """Unregister a disconnected overlay websocket client."""
        if client in self._connected_clients:
            self._connected_clients.remove(client)

    @property
    def client_count(self) -> int:
        """Number of active connected overlay windows."""
        return len(self._connected_clients)
