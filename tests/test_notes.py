import pytest
from httpx import AsyncClient

async def get_auth_token(client: AsyncClient, email: str) -> str:
    # Helper to register and login a test user
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "supersecurepassword123"}
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "supersecurepassword123"}
    )
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_note_success(client: AsyncClient):
    token = await get_auth_token(client, "notes@example.com")
    
    response = await client.post(
        "/api/v1/notes",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "First Note", "content": "This is my first note description."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "First Note"
    assert data["content"] == "This is my first note description."
    assert "id" in data
    assert "user_id" in data

@pytest.mark.asyncio
async def test_get_notes_and_search(client: AsyncClient):
    token = await get_auth_token(client, "search@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create notes
    await client.post("/api/v1/notes", headers=headers, json={"title": "Apple Note", "content": "Buy some apples"})
    await client.post("/api/v1/notes", headers=headers, json={"title": "Banana Note", "content": "Buy some bananas"})
    
    # List notes
    list_res = await client.get("/api/v1/notes", headers=headers)
    assert len(list_res.json()) == 2
    
    # Search notes
    search_res = await client.get("/api/v1/notes?search=apple", headers=headers)
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["title"] == "Apple Note"

@pytest.mark.asyncio
async def test_note_ownership_isolation(client: AsyncClient):
    token_a = await get_auth_token(client, "user_a@example.com")
    token_b = await get_auth_token(client, "user_b@example.com")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # User A creates note
    create_res = await client.post(
        "/api/v1/notes", headers=headers_a, json={"title": "Secret Note", "content": "Top secret content"}
    )
    note_id = create_res.json()["id"]
    
    # User B attempts to access User A's note
    get_res = await client.get(f"/api/v1/notes/{note_id}", headers=headers_b)
    assert get_res.status_code == 404  # Service returns 404 for tenant isolation
    
    # User B attempts to delete User A's note
    del_res = await client.delete(f"/api/v1/notes/{note_id}", headers=headers_b)
    assert del_res.status_code == 404

@pytest.mark.asyncio
async def test_update_and_delete_note(client: AsyncClient):
    token = await get_auth_token(client, "crud@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create
    note = (await client.post(
        "/api/v1/notes", headers=headers, json={"title": "Old Title", "content": "Old Content"}
    )).json()
    note_id = note["id"]
    
    # Update
    update_res = await client.put(
        f"/api/v1/notes/{note_id}", headers=headers, json={"title": "New Title"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "New Title"
    assert update_res.json()["content"] == "Old Content"  # unchanged
    
    # Delete
    del_res = await client.delete(f"/api/v1/notes/{note_id}", headers=headers)
    assert del_res.status_code == 204
    
    # Verify deleted
    get_res = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get_res.status_code == 404
