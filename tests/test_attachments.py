import pytest
from httpx import AsyncClient

async def get_auth_token(client: AsyncClient, email: str) -> str:
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
async def test_upload_attachment_success(client: AsyncClient):
    token = await get_auth_token(client, "upload@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create note
    note = (await client.post(
        "/api/v1/notes", headers=headers, json={"title": "Note with Attachment", "content": "Text"}
    )).json()
    note_id = note["id"]
    
    # Upload file
    file_content = b"This is testing file content for attachments."
    files = {"file": ("test_file.txt", file_content, "text/plain")}
    
    upload_res = await client.post(
        f"/api/v1/notes/{note_id}/attachments",
        headers=headers,
        files=files
    )
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["filename"] == "test_file.txt"
    assert data["mime_type"] == "text/plain"
    assert "id" in data
    assert data["note_id"] == note_id
    
    # Verify note details now includes attachment list
    get_res = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert len(get_res.json()["attachments"]) == 1
    assert get_res.json()["attachments"][0]["filename"] == "test_file.txt"

@pytest.mark.asyncio
async def test_upload_invalid_mime_type(client: AsyncClient):
    token = await get_auth_token(client, "mime@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    note = (await client.post(
        "/api/v1/notes", headers=headers, json={"title": "Mime Note", "content": "Text"}
    )).json()
    
    # Upload invalid file (e.g. executable)
    files = {"file": ("danger.exe", b"executable bytes", "application/x-msdownload")}
    
    upload_res = await client.post(
        f"/api/v1/notes/{note['id']}/attachments",
        headers=headers,
        files=files
    )
    assert upload_res.status_code == 400
    assert "not supported" in upload_res.json()["detail"]

@pytest.mark.asyncio
async def test_upload_file_size_exceeded(client: AsyncClient, monkeypatch):
    # Temporarily monkeypatch settings max file size to 10 bytes for size testing
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 10)
    
    token = await get_auth_token(client, "size@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    note = (await client.post(
        "/api/v1/notes", headers=headers, json={"title": "Size Note", "content": "Text"}
    )).json()
    
    files = {"file": ("large.txt", b"this text content exceeds 10 bytes size", "text/plain")}
    
    upload_res = await client.post(
        f"/api/v1/notes/{note['id']}/attachments",
        headers=headers,
        files=files
    )
    assert upload_res.status_code == 400
    assert "exceeds limit" in upload_res.json()["detail"]

@pytest.mark.asyncio
async def test_download_and_delete_attachment(client: AsyncClient):
    token = await get_auth_token(client, "download@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create note and upload
    note = (await client.post(
        "/api/v1/notes", headers=headers, json={"title": "Test Note", "content": "Text"}
    )).json()
    note_id = note["id"]
    
    file_bytes = b"Hello Notes!"
    files = {"file": ("test.txt", file_bytes, "text/plain")}
    upload = (await client.post(
        f"/api/v1/notes/{note_id}/attachments", headers=headers, files=files
    )).json()
    file_id = upload["id"]
    
    # Download
    dl_res = await client.get(f"/api/v1/notes/{note_id}/attachments/{file_id}", headers=headers)
    assert dl_res.status_code == 200
    assert dl_res.content == file_bytes
    
    # Delete
    del_res = await client.delete(f"/api/v1/notes/{note_id}/attachments/{file_id}", headers=headers)
    assert del_res.status_code == 204
    
    # Verify download fails now
    dl_res_after = await client.get(f"/api/v1/notes/{note_id}/attachments/{file_id}", headers=headers)
    assert dl_res_after.status_code == 404
