import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import requests  # Import the requests module
import os  # Import the os module
from app.main import app
from app.openai_utils import generate_headline
from app.scraping import extract_images
from tests.mock_utils import set_openai_api_key, mock_openai_client
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

client = TestClient(app)

def mock_requests_get_image(*args, **kwargs):
    url = str(args[0])  # Convert the URL to a string
    if url.startswith("http://example.com/image"):
        img = Image.new('RGB', (300, 300), color=(73, 109, 137))  # Ensure the image meets the size criteria
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        response = MagicMock()
        response.content = img_byte_arr.read()
        response.status_code = 200
        return response
    else:
        response = MagicMock()
        response.content = """
        <html>
            <body>
                <p>Hello, World!</p>
                <img src="http://example.com/image1.jpg" />
                <img src="http://example.com/image2.jpg" />
            </body>
        </html>
        """
        response.status_code = 200
        return response


def test_generate_headline():
    text = "This is a sample website text."
    image_url = "http://example.com/image.jpg"
    mock_client = mock_openai_client()
    headline = generate_headline(mock_client, text, image_url)
    assert headline == "Mocked Ad Headline"
    assert len(headline.split()) <= 5  # Ensure the headline is no more than 5 words


@patch('requests.get', side_effect=mock_requests_get_image)

def test_extract_text_success(mock_get):
    url = "http://example.com"
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    expected_headlines = ["Mocked Ad Headline", "Mocked Ad Headline"]

    with patch("app.routes.OpenAI", return_value=mock_openai_client()):
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


@patch('requests.get', side_effect=mock_requests_get_image)

def test_extract_images(mock_get):
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


@patch('requests.get', side_effect=mock_requests_get_image)

def test_extract_images_with_limit(mock_get):
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

