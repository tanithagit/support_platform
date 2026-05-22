import pytest
from fastapi.testclient import TestClient


def setup_users(client):
    """Create admin, agent and customer for testing"""
    # Create admin + org
    client.post("/auth/register", json={
        "email": "admin@ticket.com",
        "password": "admin123",
        "full_name": "Admin",
        "role": "admin",
        "organization_name": "Ticket Company"
    })

    # Get admin token
    admin_login = client.post("/auth/login", json={
        "email": "admin@ticket.com",
        "password": "admin123"
    })
    admin_token = admin_login.json()["access_token"]
    admin_header = {"Authorization": f"Bearer {admin_token}"}

    # Get org id
    admin_data = admin_login.json()["user"]
    org_id = admin_data["organization_id"]

    # Create customer
    client.post("/auth/register", json={
        "email": "customer@ticket.com",
        "password": "customer123",
        "full_name": "Customer",
        "role": "customer",
        "organization_id": org_id
    })

    customer_login = client.post("/auth/login", json={
        "email": "customer@ticket.com",
        "password": "customer123"
    })
    customer_token = customer_login.json()["access_token"]
    customer_header = {"Authorization": f"Bearer {customer_token}"}

    # Create agent
    client.post("/users/agents",
        json={
            "email": "agent@ticket.com",
            "password": "agent123",
            "full_name": "Agent"
        },
        headers=admin_header
    )

    agent_login = client.post("/auth/login", json={
        "email": "agent@ticket.com",
        "password": "agent123"
    })
    agent_token = agent_login.json()["access_token"]
    agent_header = {"Authorization": f"Bearer {agent_token}"}

    return admin_header, customer_header, agent_header


def test_create_ticket(client: TestClient):
    """Test customer can create a ticket"""
    admin_h, customer_h, agent_h = setup_users(client)

    response = client.post("/tickets/", json={
        "subject": "Test ticket",
        "description": "This is a test ticket",
        "priority": "medium"
    }, headers=customer_h)

    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Test ticket"
    assert data["status"] in ["open", "in_progress"]
    assert data["priority"] == "medium"
    print("✅ Ticket creation passed")


def test_customer_sees_only_own_tickets(client: TestClient):
    """Test customer can only see their own tickets"""
    admin_h, customer_h, agent_h = setup_users(client)

    # Create ticket as customer
    client.post("/tickets/", json={
        "subject": "My ticket",
        "description": "My issue",
        "priority": "low"
    }, headers=customer_h)

    # Get tickets as customer
    response = client.get("/tickets/", headers=customer_h)
    assert response.status_code == 200
    tickets = response.json()

    # All tickets should belong to this customer
    customer_res = client.get("/auth/me", headers=customer_h)
    customer_id = customer_res.json()["id"]

    for ticket in tickets:
        assert ticket["customer_id"] == customer_id
    print("✅ Customer sees only own tickets passed")


def test_status_transition_valid(client: TestClient):
    """Test valid status transition open → in_progress"""
    admin_h, customer_h, agent_h = setup_users(client)

    # Create ticket
    ticket_res = client.post("/tickets/", json={
        "subject": "Status test",
        "description": "Testing status",
        "priority": "high"
    }, headers=customer_h)
    ticket_id = ticket_res.json()["id"]

    # Get ticket to check current status
    ticket = client.get(f"/tickets/{ticket_id}", headers=admin_h).json()

    # Try valid transition
    if ticket["status"] == "open":
        response = client.patch(
            f"/tickets/{ticket_id}/status",
            json={"status": "in_progress"},
            headers=agent_h
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
    print("✅ Valid status transition passed")


def test_status_transition_invalid(client: TestClient):
    """Test invalid status transition is rejected"""
    admin_h, customer_h, agent_h = setup_users(client)

    # Create ticket (starts as open or in_progress)
    ticket_res = client.post("/tickets/", json={
        "subject": "Invalid transition test",
        "description": "Testing invalid transition",
        "priority": "low"
    }, headers=customer_h)
    ticket_id = ticket_res.json()["id"]

    # Try to jump from open directly to closed (invalid)
    response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={"status": "closed"},
        headers=admin_h
    )
    assert response.status_code == 400
    print("✅ Invalid status transition rejection passed")


def test_admin_can_assign_ticket(client: TestClient):
    """Test admin can assign ticket to agent"""
    admin_h, customer_h, agent_h = setup_users(client)

    # Create ticket
    ticket_res = client.post("/tickets/", json={
        "subject": "Assign test",
        "description": "Test assignment",
        "priority": "urgent"
    }, headers=customer_h)
    ticket_id = ticket_res.json()["id"]

    # Get agent id
    agent_res = client.get("/auth/me", headers=agent_h)
    agent_id = agent_res.json()["id"]

    # Assign ticket
    response = client.post(
        f"/tickets/{ticket_id}/assign",
        json={"agent_id": agent_id},
        headers=admin_h
    )
    assert response.status_code == 200
    assert response.json()["assigned_to"] == agent_id
    print("✅ Ticket assignment passed")


def test_customer_cannot_assign_ticket(client: TestClient):
    """Test customer cannot assign tickets"""
    admin_h, customer_h, agent_h = setup_users(client)

    ticket_res = client.post("/tickets/", json={
        "subject": "No assign test",
        "description": "Test",
        "priority": "low"
    }, headers=customer_h)
    ticket_id = ticket_res.json()["id"]

    # Customer tries to assign — should fail
    response = client.post(
        f"/tickets/{ticket_id}/assign",
        json={"agent_id": 1},
        headers=customer_h
    )
    assert response.status_code == 403
    print("✅ Customer cannot assign ticket passed")


def test_dashboard_stats(client: TestClient):
    """Test dashboard returns correct stats"""
    admin_h, customer_h, agent_h = setup_users(client)

    # Create some tickets
    for i in range(3):
        client.post("/tickets/", json={
            "subject": f"Ticket {i}",
            "description": f"Description {i}",
            "priority": "medium"
        }, headers=customer_h)

    response = client.get("/tickets/dashboard", headers=admin_h)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "open" in data
    assert "in_progress" in data
    assert data["total"] >= 3
    print("✅ Dashboard stats passed")