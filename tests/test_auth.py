import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "supersecurepassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    # Register first user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "supersecurepassword123"}
    )
    # Register duplicate user
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "anotherpassword123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists."

@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "short"}
    )
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "supersecurepassword123"}
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "supersecurepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "supersecurepassword123"}
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "profile@example.com", "password": "supersecurepassword123"}
    )
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "profile@example.com", "password": "supersecurepassword123"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    profile_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "profile@example.com"
