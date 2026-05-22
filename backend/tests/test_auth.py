import pytest
from fastapi.testclient import TestClient


def test_register_admin(client: TestClient):
    """Test admin registration with new organization"""
    response = client.post("/auth/register", json={
        "email": "admin@test.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin",
        "organization_name": "Test Company"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"
    assert data["organization_id"] is not None
    print("✅ Admin registration passed")


def test_register_customer(client: TestClient):
    """Test customer registration joining existing org"""
    # First create org via admin
    client.post("/auth/register", json={
        "email": "admin2@test.com",
        "password": "admin123",
        "full_name": "Admin",
        "role": "admin",
        "organization_name": "Company 2"
    })

    # Register customer in same org
    response = client.post("/auth/register", json={
        "email": "customer@test.com",
        "password": "customer123",
        "full_name": "Test Customer",
        "role": "customer",
        "organization_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "customer"
    print("✅ Customer registration passed")


def test_register_duplicate_email(client: TestClient):
    """Test that duplicate email is rejected"""
    client.post("/auth/register", json={
        "email": "same@test.com",
        "password": "pass123",
        "full_name": "User 1",
        "role": "admin",
        "organization_name": "Company A"
    })

    # Try to register same email again
    response = client.post("/auth/register", json={
        "email": "same@test.com",
        "password": "pass456",
        "full_name": "User 2",
        "role": "customer",
        "organization_id": 1
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
    print("✅ Duplicate email rejection passed")


def test_login_success(client: TestClient):
    """Test successful login returns JWT token"""
    client.post("/auth/register", json={
        "email": "login@test.com",
        "password": "password123",
        "full_name": "Login User",
        "role": "admin",
        "organization_name": "Login Company"
    })

    response = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@test.com"
    print("✅ Login success passed")


def test_login_wrong_password(client: TestClient):
    """Test login with wrong password is rejected"""
    client.post("/auth/register", json={
        "email": "wrong@test.com",
        "password": "correct123",
        "full_name": "Test User",
        "role": "admin",
        "organization_name": "Wrong Co"
    })

    response = client.post("/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    print("✅ Wrong password rejection passed")


def test_get_me(client: TestClient):
    """Test getting current user info"""
    client.post("/auth/register", json={
        "email": "me@test.com",
        "password": "me123",
        "full_name": "Me User",
        "role": "admin",
        "organization_name": "Me Company"
    })

    login_res = client.post("/auth/login", json={
        "email": "me@test.com",
        "password": "me123"
    })
    token = login_res.json()["access_token"]

    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"
    print("✅ Get current user passed")


def test_get_me_without_token(client: TestClient):
    """Test that protected route requires token"""
    response = client.get("/auth/me")
    assert response.status_code in [401, 403]
    print("✅ Unauthorized access rejection passed")