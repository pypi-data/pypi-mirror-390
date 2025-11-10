import pytest
from fastapi.testclient import TestClient
from main import app, UPLOAD_DIR
import os
import shutil
import asyncio
import json

# Create a client for testing
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Fixture to set up a clean upload directory for tests and tear it down afterward."""
    # Ensure a clean state before tests run
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir()

    # Yield control to the tests
    yield

    # Teardown: clean up the uploads directory after all tests in the module are done
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)

def test_upload_file():
    """Test basic file upload."""
    response = client.post(
        "/upload",
        files={"file": ("test_file.txt", b"hello world", "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "test_file.txt"
    assert "url" in data
    assert "file_id" in data

def test_upload_with_password():
    """Test file upload with a password."""
    response = client.post(
        "/upload",
        files={"file": ("test_password.txt", b"secret content", "text/plain")},
        data={"hours": "1", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["password_protected"] is True

def test_download_file_no_password():
    """Test downloading a file that doesn't require a password."""
    # First, upload a file
    upload_response = client.post(
        "/upload",
        files={"file": ("download_test.txt", b"download content", "text/plain")},
        data={"hours": "1"},
    )
    upload_data = upload_response.json()
    file_url = upload_data["url"]

    # Now, try to download it
    # The URL contains the full host, so we need to extract the path
    path = file_url.split("/", 3)[-1]
    download_response = client.get(path)

    assert download_response.status_code == 200
    assert download_response.content == b"download content"

def test_download_file_with_correct_password():
    """Test downloading a password-protected file with the correct password."""
    upload_response = client.post(
        "/upload",
        files={"file": ("protected_download.txt", b"protected", "text/plain")},
        data={"hours": "1", "password": "supersecret"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    download_response = client.get(f"{path}?password=supersecret")
    assert download_response.status_code == 200
    assert download_response.content == b"protected"

def test_download_file_with_incorrect_password():
    """Test downloading a password-protected file with an incorrect password."""
    upload_response = client.post(
        "/upload",
        files={"file": ("protected_fail.txt", b"protected fail", "text/plain")},
        data={"hours": "1", "password": "supersecret"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    download_response = client.get(f"{path}?password=wrongpassword")
    assert download_response.status_code == 403 # Forbidden

def test_one_time_download():
    """Test that a one-time download file is deleted after being accessed."""
    upload_response = client.post(
        "/upload",
        files={"file": ("one_time.txt", b"one time content", "text/plain")},
        data={"hours": "1", "one_time": "true"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    # First download should succeed
    first_download_response = client.get(path)
    assert first_download_response.status_code == 200

    # Let the async deletion task run
    async def wait_for_deletion():
        await asyncio.sleep(0.1)

    asyncio.run(wait_for_deletion())

    # Second download should fail
    second_download_response = client.get(path)
    assert second_download_response.status_code == 404 # Not Found

def test_delete_file():
    """Test deleting a file using the client_id."""
    # Upload a file with a specific client_id
    client_id = "test-client-123"
    upload_response = client.post(
        "/upload",
        files={"file": ("to_be_deleted.txt", b"delete me", "text/plain")},
        data={"hours": "1", "client_id": client_id},
    )
    upload_data = upload_response.json()
    file_id = upload_data["file_id"]

    # Now, delete the file with the correct client_id
    delete_response = client.request(
        "DELETE",
        f"/delete/{file_id}",
        json={"client_id": client_id},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True

    # Verify the file is gone
    path = upload_data["url"].split("/", 3)[-1]
    get_response = client.get(path)
    assert get_response.status_code == 404

def test_delete_file_unauthorized():
    """Test that deleting a file with the wrong client_id fails."""
    # Upload a file with a specific client_id
    owner_client_id = "owner-client"
    upload_response = client.post(
        "/upload",
        files={"file": ("unauthorized_delete.txt", b"don't delete me", "text/plain")},
        data={"hours": "1", "client_id": owner_client_id},
    )
    upload_data = upload_response.json()
    file_id = upload_data["file_id"]

    # Attempt to delete with a different client_id
    attacker_client_id = "attacker-client"
    delete_response = client.request(
        "DELETE",
        f"/delete/{file_id}",
        json={"client_id": attacker_client_id},
    )
    assert delete_response.status_code == 403 # Forbidden
