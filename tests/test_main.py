import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_response(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse(b"<html><body><p>Hello, World!</p></body></html>")

    monkeypatch.setattr("requests.get", mock_get)

def test_extract_text_success(mock_response):
    response = client.post("/extract-text", json={"url": "http://example.com"})
    assert response.status_code == 200
    assert response.json() == {"text": "Hello, World!"}

def test_extract_text_invalid_url():
    response = client.post("/extract-text", json={"url": "http://invalid-url"})
    assert response.status_code == 400
    assert "Failed to resolve" in response.json()["detail"]
