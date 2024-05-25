import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import requests
from app.main import app
from tests.mock_utils import mock_openai_client
from io import BytesIO
from PIL import Image

client = TestClient(app)

def mock_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            pass

    url = str(args[0])  # Convert Url object to string
    if url.startswith("http://example.com/image"):
        img = Image.new('RGB', (300, 250), color=(73, 109, 137))  # Updated size to meet new requirements
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return MockResponse(img_byte_arr.read())
    else:
        return MockResponse("""
        <html>
            <body>
                <p>Hello, World!</p>
                <img src="http://example.com/image1.jpg" />
                <img src="http://example.com/image2.jpg" />
            </body>
        </html>
        """)

@patch('requests.get', side_effect=mock_requests_get)
@patch("app.routes.OpenAI", return_value=mock_openai_client())
def test_extract_text_success(mock_get, mock_openai):
    url = "http://example.com"
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    expected_headlines = ["Mocked Ad Headline", "Mocked Ad Headline"]

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
