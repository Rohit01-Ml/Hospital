"""WebSocket connection manager for live queue updates."""
from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # room_id (e.g. "doctor_d1") -> list of active WebSocket connections
        self._rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        self._rooms.setdefault(room_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self._rooms:
            self._rooms[room_id] = [
                ws for ws in self._rooms[room_id] if ws != websocket
            ]

    async def broadcast(self, room_id: str, data: dict):
        """Send JSON to every client subscribed to room_id."""
        dead: List[WebSocket] = []
        for ws in self._rooms.get(room_id, []):
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, room_id)

    def subscriber_count(self, room_id: str) -> int:
        return len(self._rooms.get(room_id, []))


# Singleton used across the app
manager = ConnectionManager()
