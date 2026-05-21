from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    """
    Manages all active WebSocket connections.
    Each ticket has its own list of connected users.
    """

    def __init__(self):
        # Dict of ticket_id -> list of connected websockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, ticket_id: int):
        """Accept a new WebSocket connection for a ticket"""
        await websocket.accept()

        if ticket_id not in self.active_connections:
            self.active_connections[ticket_id] = []

        self.active_connections[ticket_id].append(websocket)
        print(f"New connection for ticket {ticket_id}. "
              f"Total: {len(self.active_connections[ticket_id])}")

    def disconnect(self, websocket: WebSocket, ticket_id: int):
        """Remove a WebSocket connection"""
        if ticket_id in self.active_connections:
            self.active_connections[ticket_id].remove(websocket)
            print(f"Disconnected from ticket {ticket_id}. "
                  f"Remaining: {len(self.active_connections[ticket_id])}")

    async def broadcast_to_ticket(self, ticket_id: int, message: dict):
        """Send message to ALL users connected to a ticket"""
        if ticket_id not in self.active_connections:
            return

        # Send to each connected user
        disconnected = []
        for connection in self.active_connections[ticket_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Connection is broken, mark for removal
                disconnected.append(connection)

        # Clean up broken connections
        for conn in disconnected:
            self.active_connections[ticket_id].remove(conn)

    async def send_personal_message(
        self, websocket: WebSocket, message: dict
    ):
        """Send message to a single user"""
        await websocket.send_text(json.dumps(message))


# Global instance — shared across the entire app
manager = ConnectionManager()