import pytest
from fastapi.testclient import TestClient


def setup_ticket(client):
    """Create users and a ticket for chat testing"""
    # Admin + org
    client.post("/auth/register", json={
        "email": "admin@chat.com",
        "password": "admin123",
        "full_name": "Admin",
        "role": "admin",
        "organization_name": "Chat Company"
    })
    admin_login = client.post("/auth/login", json={
        "email": "admin@chat.com", "password": "admin123"
    })
    admin_header = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    org_id = admin_login.json()["user"]["organization_id"]

    # Customer
    client.post("/auth/register", json={
        "email": "customer@chat.com",
        "password": "customer123",
        "full_name": "Chat Customer",
        "role": "customer",
        "organization_id": org_id
    })
    customer_login = client.post("/auth/login", json={
        "email": "customer@chat.com", "password": "customer123"
    })
    customer_header = {"Authorization": f"Bearer {customer_login.json()['access_token']}"}

    # Create ticket
    ticket_res = client.post("/tickets/", json={
        "subject": "Chat test ticket",
        "description": "Testing chat",
        "priority": "high"
    }, headers=customer_header)
    ticket_id = ticket_res.json()["id"]

    return admin_header, customer_header, ticket_id


def test_get_messages_empty(client: TestClient):
    """Test getting messages for new ticket"""
    admin_h, customer_h, ticket_id = setup_ticket(client)

    response = client.get(
        f"/tickets/{ticket_id}/messages",
        headers=customer_h
    )
    assert response.status_code == 200
    messages = response.json()
    # Should have auto-response message
    assert len(messages) >= 1
    # First message should be auto-response
    assert messages[0]["is_auto_response"] == True
    print("✅ Auto-response message on ticket creation passed")


def test_auto_response_content(client: TestClient):
    """Test auto-response contains ticket ID"""
    admin_h, customer_h, ticket_id = setup_ticket(client)

    response = client.get(
        f"/tickets/{ticket_id}/messages",
        headers=customer_h
    )
    messages = response.json()
    auto_msg = messages[0]

    assert str(ticket_id) in auto_msg["content"]
    assert auto_msg["is_auto_response"] == True
    print("✅ Auto-response content passed")


def test_send_message_via_http(client: TestClient):
    """Test sending message via HTTP endpoint"""
    admin_h, customer_h, ticket_id = setup_ticket(client)

    response = client.post(
        f"/tickets/{ticket_id}/messages",
        params={"content": "Hello from customer!"},
        headers=customer_h
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello from customer!"
    assert data["ticket_id"] == ticket_id
    print("✅ Send message via HTTP passed")


def test_customer_cannot_access_other_ticket_chat(client: TestClient):
    """Test customer cannot read chat from another customer's ticket"""
    admin_h, customer_h, ticket_id = setup_ticket(client)

    # Create another customer
    org_id = client.get("/auth/me", headers=customer_h).json()["organization_id"]
    client.post("/auth/register", json={
        "email": "other@chat.com",
        "password": "other123",
        "full_name": "Other Customer",
        "role": "customer",
        "organization_id": org_id
    })
    other_login = client.post("/auth/login", json={
        "email": "other@chat.com", "password": "other123"
    })
    other_header = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    # Other customer tries to read first customer's chat
    response = client.get(
        f"/tickets/{ticket_id}/messages",
        headers=other_header
    )
    assert response.status_code == 403
    print("✅ Chat access control passed")