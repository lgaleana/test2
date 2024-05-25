import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests
from app.main import app

client = TestClient(app)

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
