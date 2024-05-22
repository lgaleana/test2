import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import requests  # Import the requests module
from app.main import app

client = TestClient(app)


def mock_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code != 200:
                raise requests.RequestException("Request failed")

    if args[0] == "http://example.com/image.jpg":
        return MockResponse(b"fake_image_data", 200)
    return MockResponse(None, 404)


def test_download_image_success():
    url = "http://example.com/image.jpg"
    text = "Sample Text"
    x, y = 10, 10

    with patch("requests.get", side_effect=mock_requests_get):
        response = client.get("/download-image", params={"url": url, "text": text, "x": x, "y": y})
        print(response.json())  # Add this line to print the response for debugging
        assert response.status_code == 200
        assert response.headers["Content-Disposition"] == "attachment; filename=overlayed_image.png"
        assert response.headers["Content-Type"] == "image/png"


def test_download_image_invalid_url():
    response = client.get("/download-image", params={"url": "invalid-url", "text": "Sample Text", "x": 10, "y": 10})
    assert response.status_code == 422


def test_download_image_request_exception():
    url = "http://example.com/image.jpg"
    text = "Sample Text"
    x, y = 10, 10

    with patch("requests.get", side_effect=requests.RequestException("Request failed")):
        response = client.get("/download-image", params={"url": url, "text": text, "x": x, "y": y})
        assert response.status_code == 400
        assert response.json() == {"detail": "Request failed"}
