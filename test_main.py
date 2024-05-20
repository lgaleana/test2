import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests
from app.main import app

client = TestClient(app)


def test_extract_text_success():
    url = "http://example.com"
    html_content = "<html><body><p>Hello, World!</p><img src='http://example.com/image.jpg'></body></html>"
    expected_text = "Hello, World!"
    expected_headline = "Sample Headline"

    with patch("requests.get") as mock_get, patch("openai.ChatCompletion.create") as mock_openai:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = html_content
        mock_openai.return_value.choices = [type('', (), {'message': {'content': expected_headline}})()]

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert response.json() == {
            "text": expected_text,
            "headlines": [{"image_url": "http://example.com/image.jpg", "headline": expected_headline}]
        }


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

    with patch("requests.get") as mock_get, patch("openai.ChatCompletion.create") as mock_openai:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = "<html><body><p>Sample Text</p><img src='https://thinkingofbermuda.com/sample.jpg'></body></html>"
        mock_openai.return_value.choices = [type('', (), {'message': {'content': "Sample Headline"}})()]

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert "text" in response.json()
        assert "headlines" in response.json()
        assert len(response.json()["headlines"]) > 0
