import pytest
from fastapi.testclient import TestClient


def setup_all_users(client):
    """Setup all user types"""
    # Admin + org
    client.post("/auth/register", json={
        "email": "admin@roles.com",
        "password": "admin123",
        "full_name": "Admin",
        "role": "admin",
        "organization_name": "Roles Company"
    })
    admin_login = client.post("/auth/login", json={
        "email": "admin@roles.com", "password": "admin123"
    })
    admin_token = admin_login.json()["access_token"]
    admin_header = {"Authorization": f"Bearer {admin_token}"}
    org_id = admin_login.json()["user"]["organization_id"]

    # Customer
    client.post("/auth/register", json={
        "email": "customer@roles.com",
        "password": "customer123",
        "full_name": "Customer",
        "role": "customer",
        "organization_id": org_id
    })
    customer_login = client.post("/auth/login", json={
        "email": "customer@roles.com", "password": "customer123"
    })
    customer_token = customer_login.json()["access_token"]
    customer_header = {"Authorization": f"Bearer {customer_token}"}

    # Agent
    client.post("/users/agents",
        json={"email": "agent@roles.com", "password": "agent123", "full_name": "Agent"},
        headers=admin_header
    )
    agent_login = client.post("/auth/login", json={
        "email": "agent@roles.com", "password": "agent123"
    })
    agent_token = agent_login.json()["access_token"]
    agent_header = {"Authorization": f"Bearer {agent_token}"}

    return admin_header, customer_header, agent_header, org_id


def test_only_admin_can_create_agent(client: TestClient):
    """Test only admin can create agents"""
    admin_h, customer_h, agent_h, org_id = setup_all_users(client)

    # Customer tries to create agent — should fail
    response = client.post("/users/agents", json={
        "email": "newagent@test.com",
        "password": "pass123",
        "full_name": "New Agent"
    }, headers=customer_h)
    assert response.status_code == 403
    print("✅ Only admin can create agent passed")


def test_agent_sees_only_assigned_tickets(client: TestClient):
    """Test agent only sees tickets assigned to them"""
    admin_h, customer_h, agent_h, org_id = setup_all_users(client)

    # Create ticket
    client.post("/tickets/", json={
        "subject": "Agent test",
        "description": "Test",
        "priority": "medium"
    }, headers=customer_h)

    # Agent gets tickets
    response = client.get("/tickets/", headers=agent_h)
    assert response.status_code == 200
    tickets = response.json()

    # Get agent id
    agent_res = client.get("/auth/me", headers=agent_h)
    agent_id = agent_res.json()["id"]

    # All tickets should be assigned to this agent
    for ticket in tickets:
        assert ticket["assigned_to"] == agent_id
    print("✅ Agent sees only assigned tickets passed")


def test_users_cannot_access_other_org_data(client: TestClient):
    """Test users cannot see other organization's data"""
    # Create first org with customer
    client.post("/auth/register", json={
        "email": "org1admin@test.com",
        "password": "pass123",
        "full_name": "Org1 Admin",
        "role": "admin",
        "organization_name": "Org One"
    })
    org1_login = client.post("/auth/login", json={
        "email": "org1admin@test.com", "password": "pass123"
    })
    org1_id = org1_login.json()["user"]["organization_id"]

    # Create second org
    client.post("/auth/register", json={
        "email": "org2admin@test.com",
        "password": "pass123",
        "full_name": "Org2 Admin",
        "role": "admin",
        "organization_name": "Org Two"
    })
    org2_login = client.post("/auth/login", json={
        "email": "org2admin@test.com", "password": "pass123"
    })
    org2_header = {"Authorization": f"Bearer {org2_login.json()['access_token']}"}
    org2_id = org2_login.json()["user"]["organization_id"]

    # Create customer in org2
    client.post("/auth/register", json={
        "email": "cust2@test.com",
        "password": "pass123",
        "full_name": "Cust2",
        "role": "customer",
        "organization_id": org2_id
    })
    cust2_login = client.post("/auth/login", json={
        "email": "cust2@test.com", "password": "pass123"
    })
    cust2_header = {"Authorization": f"Bearer {cust2_login.json()['access_token']}"}

    # Customer from org2 tries to access org1 members
    response = client.get(
        f"/organizations/{org1_id}/members",
        headers=cust2_header
    )
    assert response.status_code == 403
    print("✅ Cross-org data isolation passed")

def test_unauthenticated_cannot_access_tickets(client: TestClient):
    """Test unauthenticated users cannot access tickets"""
    response = client.get("/tickets/")
    assert response.status_code in [401, 403]
    print("✅ Unauthenticated access rejection passed")