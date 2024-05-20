import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests
from app.main import app

client = TestClient(app)


def test_extract_text_success():
    url = "http://example.com"
    html_content = """
    <html>
        <body>
            <p>Hello, World!</p>
            <img src="http://example.com/image1.jpg" />
            <img src="http://example.com/image2.jpg" />
        </body>
    </html>
    """
    expected_text = "Hello, World!"
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = html_content

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert response.json() == {"text": expected_text, "images": expected_images}


def test_extract_text_invalid_url():
    response = client.get("/extract-text", params={"url": "invalid-url"})
    assert response.status_code == 422


def test_extract_text_request_exception():
    url = "http://example.com"

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Request failed")

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 400
        assert response.json() == {"detail": "Request failed"}


def test_extract_text_bermuda():
    url = "https://thinkingofbermuda.com"
    
    response = client.get("/extract-text", params={"url": url})
    assert response.status_code == 200
    assert "text" in response.json()
    assert "images" in response.json()
