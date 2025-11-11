import pytest
from fastapi.testclient import TestClient
from main import app, UPLOAD_DIR
import os
import shutil
import asyncio
import json

# Create a client for testing
client = TestClient(app)

# Import RateLimiter to reset it
from main import RateLimiter, RATE_LIMIT_UPLOADS, RATE_LIMIT_DOWNLOADS, RATE_LIMIT_WINDOW

@pytest.fixture(autouse=True)
def reset_rate_limiters(monkeypatch):
    """Fixture to reset rate limiters before each test to prevent test interference."""
    monkeypatch.setattr("main.upload_limiter", RateLimiter(RATE_LIMIT_UPLOADS, RATE_LIMIT_WINDOW))
    monkeypatch.setattr("main.download_limiter", RateLimiter(RATE_LIMIT_DOWNLOADS, RATE_LIMIT_WINDOW))


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

def test_duplicate_file_upload():
    """Test that uploading a file with the same content hash returns the original file's URL."""
    # First upload
    response1 = client.post(
        "/upload",
        files={"file": ("duplicate_content.txt", b"this content is the same", "text/plain")},
        data={"hours": "1"},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["success"] is True

    # Second upload with the same content
    response2 = client.post(
        "/upload",
        files={"file": ("another_name.txt", b"this content is the same", "text/plain")},
        data={"hours": "1"},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True

    # Check that the file_id is the same for both uploads
    assert data1["file_id"] == data2["file_id"]

import hashlib

def calculate_hash(content: bytes) -> str:
    """Helper function to calculate SHA256 hash."""
    return hashlib.sha256(content).hexdigest()

def test_upload_with_matching_hash():
    """Test that a file upload with a matching client_hash is successful."""
    file_content = b"content for hash test"
    client_hash = calculate_hash(file_content)

    response = client.post(
        "/upload",
        files={"file": ("hash_match.txt", file_content, "text/plain")},
        data={"hours": "1", "client_hash": client_hash},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["hash_verified"] is True

def test_upload_with_mismatching_hash():
    """Test that a file upload with a mismatching client_hash is rejected."""
    file_content = b"content for hash mismatch test"
    # Provide a deliberately incorrect hash
    incorrect_hash = "thisisnotthecorrecthash" * 2

    response = client.post(
        "/upload",
        files={"file": ("hash_mismatch.txt", file_content, "text/plain")},
        data={"hours": "1", "client_hash": incorrect_hash},
    )
    assert response.status_code == 400  # Bad Request
    data = response.json()
    assert "Hash verification failed" in data["detail"]

def test_upload_rate_limiting():
    """Test that the upload rate limit is enforced."""
    # The default rate limit is 10 uploads per hour. We'll exceed this.
    for i in range(10):
        response = client.post(
            "/upload",
            files={"file": (f"rate_limit_test_{i}.txt", b"rate limit content", "text/plain")},
            data={"hours": "1"},
        )
        assert response.status_code == 200

    # The 11th request should be rate-limited
    response = client.post(
        "/upload",
        files={"file": ("rate_limit_exceeded.txt", b"this should fail", "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 429

def test_download_rate_limiting():
    """Test that the download rate limit is enforced."""
    # First, upload a file to download
    upload_response = client.post(
        "/upload",
        files={"file": ("download_rate_limit.txt", b"download me", "text/plain")},
        data={"hours": "1"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    # The default download limit is 100 per hour.
    # We will hit the endpoint 100 times, expecting success.
    for _ in range(100):
        download_response = client.get(path)
        assert download_response.status_code == 200

    # The 101st request should be rate-limited
    final_download_response = client.get(path)
    assert final_download_response.status_code == 429

def test_debug_stats_unauthorized():
    """Test that the /debug/stats endpoint requires authentication."""
    response = client.get("/debug/stats")
    assert response.status_code == 401  # Unauthorized

def test_debug_stats_authorized():
    """Test that the /debug/stats endpoint returns data with correct authentication."""
    # First, upload a file to have some stats to check
    client.post(
        "/upload",
        files={"file": ("stats_test_file.txt", b"some data", "text/plain")},
        data={"hours": "1"},
    )

    response = client.get("/debug/stats", auth=("admin", "testpassword"))
    assert response.status_code == 200
    # Check for some expected keys in the HTML response content
    assert b"Total Files" in response.content
    assert b"Total Size" in response.content
    assert b"stats_test_file.txt" in response.content

def test_debug_wipe_unauthorized():
    """Test that the /debug/wipe endpoint requires authentication."""
    response = client.post("/debug/wipe")
    assert response.status_code == 401  # Unauthorized

def test_debug_wipe_authorized():
    """Test that the /debug/wipe endpoint successfully deletes all data."""
    # First, upload a file to ensure there is data to wipe
    upload_response = client.post(
        "/upload",
        files={"file": ("wipe_test_file.txt", b"wipe me", "text/plain")},
        data={"hours": "1"},
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    # Now, wipe the data
    wipe_response = client.post("/debug/wipe", auth=("admin", "testpassword"))
    assert wipe_response.status_code == 200
    wipe_data = wipe_response.json()
    assert wipe_data["success"] is True
    assert wipe_data["wiped_files"] > 0

    # Verify that the previously uploaded file is gone
    get_response = client.get(path)
    assert get_response.status_code == 404

# Import necessary modules for the expiration test
from datetime import datetime, timedelta, timezone
from main import cleanup_expired_files, shutdown_event

@pytest.mark.asyncio
async def test_file_expiration_and_cleanup(monkeypatch):
    """Test that an expired file is automatically cleaned up by the background task."""
    # Prevent the main app's cleanup task from running automatically
    async def do_nothing():
        pass
    monkeypatch.setattr("main.cleanup_expired_files", do_nothing)

    # Set a very short cleanup interval so we can trigger it manually
    monkeypatch.setattr("main.CLEANUP_INTERVAL", 0.01)

    # Upload a file with a 1-hour expiry
    upload_response = client.post(
        "/upload",
        files={"file": ("cleanup_test.txt", b"I will be cleaned up", "text/plain")},
        data={"hours": "1"},
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]
    file_id = upload_data["file_id"]

    # At this point, the file should exist in the metadata
    from main import metadata
    assert file_id in metadata

    # A mock datetime class that is always 2 hours in the future
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(timezone.utc) + timedelta(hours=2)

    # Now, patch the datetime object to simulate time passing
    monkeypatch.setattr('main.datetime', MockDateTime)

    # Manually run the cleanup task once
    # Reset the shutdown event to allow the task to run
    shutdown_event.clear()
    cleanup_task = asyncio.create_task(cleanup_expired_files())
    await asyncio.sleep(0.02) # Give it a moment to run
    shutdown_event.set() # Stop the task
    await cleanup_task # Wait for it to finish gracefully

    # After cleanup, the file should be gone from metadata and disk
    assert file_id not in metadata
    download_response = client.get(path)
    assert download_response.status_code == 404

def test_upload_with_invalid_expiry():
    """Test that uploading with an invalid expiry time fails."""
    response = client.post(
        "/upload",
        files={"file": ("invalid_expiry.txt", b"some content", "text/plain")},
        data={"hours": "999"},  # 999 is not a valid expiry option
    )
    assert response.status_code == 400
    assert "Invalid expiry time" in response.json()["detail"]

def test_upload_exceeding_max_size(monkeypatch):
    """Test that uploading a file larger than MAX_FILE_SIZE fails."""
    # Set a very small max file size for the test
    monkeypatch.setattr("main.MAX_FILE_SIZE", 10) # 10 bytes

    # Attempt to upload a file larger than the new max size
    file_content = b"this file is definitely larger than ten bytes"
    response = client.post(
        "/upload",
        files={"file": ("too_large.txt", file_content, "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 413 # Payload Too Large
    assert "File too large" in response.json()["detail"]
