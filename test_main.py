import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests
from app.main import app

client = TestClient(app)


def test_extract_text_success():
    url = "http://example.com"
    html_content = "<html><body><p>Hello, World!</p></body></html>"
    expected_text = "Hello, World!"

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = html_content

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert response.json() == {"text": expected_text}


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
    html_content = "<html><body><p>Welcome to Bermuda!</p></body></html>"
    expected_text = "Welcome to Bermuda!"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = html_content
        mock_get.return_value.headers = headers

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert response.json() == {"text": expected_text}
