import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests
from app.main import app
from mock_utils import mock_openai_client

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
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    expected_headlines = ["Mocked Ad Headline", "Mocked Ad Headline"]

    with patch("requests.get") as mock_get, patch("app.routes.OpenAI", return_value=mock_openai_client()):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = html_content

        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert response.json() == {"images": expected_images, "headlines": expected_headlines}
        for headline in response.json()["headlines"]:
            assert len(headline.split()) <= 5  # Ensure each headline is no more than 5 words


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
    
    with patch("app.routes.OpenAI", return_value=mock_openai_client()):
        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert "images" in response.json()
        assert "headlines" in response.json()
        for headline in response.json()["headlines"]:
            assert len(headline.split()) <= 5  # Ensure each headline is no more than 5 words
