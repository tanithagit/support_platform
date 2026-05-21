from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect,
    Depends
)
from sqlmodel import Session
from typing import List
from app.database import get_session, engine
from app.schemas.message import MessageResponse
from app.services.message_service import (
    get_ticket_messages, save_message
)
from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.models.user import User
from app.models.ticket import Ticket
from app.websockets.chat import manager
from sqlmodel import Session as SQLSession
import json

router = APIRouter(tags=["Messages"])


# ── REST: Get chat history ───────────────────────────────
@router.get(
    "/tickets/{ticket_id}/messages",
    response_model=List[MessageResponse]
)
def get_messages(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all messages for a ticket"""
    return get_ticket_messages(ticket_id, current_user, session)


# ── REST: Send message via HTTP (backup) ─────────────────
@router.post(
    "/tickets/{ticket_id}/messages",
    response_model=MessageResponse
)
def send_message(
    ticket_id: int,
    content: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Send a message via HTTP"""
    msg = save_message(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        content=content,
        session=session
    )
    return msg


# ── WebSocket: Real-time chat ────────────────────────────
@router.websocket("/ws/{ticket_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int,
    token: str
):
    """
    WebSocket for real-time chat.
    URL: ws://localhost:8000/ws/{ticket_id}?token=YOUR_JWT
    """

    # Step 1: Verify token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001)
        return

    # Step 2: Validate user and ticket access
    with SQLSession(engine) as session:
        user = session.get(User, int(user_id))
        if not user:
            await websocket.close(code=4001)
            return

        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            await websocket.close(code=4004)
            return

        if ticket.organization_id != user.organization_id:
            await websocket.close(code=4003)
            return

        if user.role == "customer" and ticket.customer_id != user.id:
            await websocket.close(code=4003)
            return

        if user.role == "agent" and ticket.assigned_to != user.id:
            await websocket.close(code=4003)
            return

        user_name = user.full_name

    # Step 3: Accept connection
    await manager.connect(websocket, ticket_id)

    # Step 4: Send welcome
    await manager.send_personal_message(websocket, {
        "type": "system",
        "message": f"Welcome {user_name}! Connected to ticket #{ticket_id}"
    })

    # Step 5: Listen for messages
    try:
        while True:
            data = await websocket.receive_text()

            try:
                msg_data = json.loads(data)
                content = msg_data.get("content", "").strip()
            except Exception:
                content = data.strip()

            if not content:
                continue

            # Save to database
            with SQLSession(engine) as session:
                saved_msg = save_message(
                    ticket_id=ticket_id,
                    sender_id=int(user_id),
                    content=content,
                    session=session
                )

            # Broadcast to all in ticket
            await manager.broadcast_to_ticket(ticket_id, {
                "type": "message",
                "id": saved_msg.id,
                "ticket_id": ticket_id,
                "sender_id": int(user_id),
                "sender_name": user_name,
                "content": content,
                "created_at": saved_msg.created_at.isoformat()
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, ticket_id)
        await manager.broadcast_to_ticket(ticket_id, {
            "type": "system",
            "message": f"{user_name} left the chat"
        })