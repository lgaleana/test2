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
    url = "http://invalid-url"

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Invalid URL")

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid URL"}
