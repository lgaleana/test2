import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests
import os
from bs4 import BeautifulSoup
from app.main import app
from app.openai_utils import generate_headline
from app.scraping import extract_images
from test_utils import set_openai_api_key, mock_openai_client

client = TestClient(app)


def test_generate_headline():
    text = "This is a sample website text."
    image_url = "http://example.com/image.jpg"
    mock_client = mock_openai_client()
    headline = generate_headline(mock_client, text, image_url)
    assert headline == "Mocked Ad Headline"
    assert len(headline.split()) <= 5  # Ensure the headline is no more than 5 words


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

    with patch("requests.get") as mock_get, patch("app.main.OpenAI", return_value=mock_openai_client()):
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
    
    with patch("app.main.OpenAI", return_value=mock_openai_client()):
        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert "images" in response.json()
        assert "headlines" in response.json()
        for headline in response.json()["headlines"]:
            assert len(headline.split()) <= 5  # Ensure each headline is no more than 5 words


def test_extract_images():
    html_content = """
    <html>
        <body>
            <img src="http://example.com/image1.jpg" />
            <meta property="og:image" content="http://example.com/image2.jpg" />
            <link rel="image_src" href="http://example.com/image3.jpg" type="image/jpeg" />
            <source srcset="http://example.com/image4.jpg 1x, http://example.com/image5.jpg 2x" />
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    expected_images = [
        "http://example.com/image1.jpg",
        "http://example.com/image2.jpg",
        "http://example.com/image3.jpg",
        "http://example.com/image4.jpg"
    ]
    assert extract_images(soup) == expected_images


def test_extract_images_with_limit():
    html_content = """
    <html>
        <body>
            <img src="http://example.com/image1.jpg" />
            <img src="http://example.com/image2.jpg" />
            <img src="http://example.com/image3.jpg" />
            <img src="http://example.com/image4.jpg" />
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with patch.dict(os.environ, {"N_IMAGES": "2"}):
        expected_images = [
            "http://example.com/image1.jpg",
            "http://example.com/image2.jpg"
        ]
        assert extract_images(soup) == expected_images
