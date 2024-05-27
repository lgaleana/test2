import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from tests.mock_utils import mock_openai_client
from io import BytesIO
from PIL import Image
import os

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

@patch('requests.get', side_effect=mock_requests_get_image)
def test_extract_text_success_with_openai(mock_get):
    url = "http://example.com"
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    expected_headlines = ["Mocked Ad Headline", "Mocked Ad Headline"]

    with patch("app.routes.OpenAI", return_value=mock_openai_client()):
        with patch.dict(os.environ, {"USE_OPENAI_HEADLINE": "True"}):
            # Add logging to verify the environment variable
            print(f"USE_OPENAI_HEADLINE in test: {os.getenv('USE_OPENAI_HEADLINE')}")
            
            response = client.get("/extract-text", params={"url": url})
            assert response.status_code == 200
            assert response.json() == {"images": expected_images, "headlines": expected_headlines}
            for headline in response.json()["headlines"]:
                assert len(headline.split()) <= 5  # Ensure each headline is no more than 5 words

@patch('requests.get', side_effect=mock_requests_get_image)
def test_extract_text_success_without_openai(mock_get):
    url = "http://example.com"
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    expected_headlines = ["Ad headline", "Ad headline"]

    with patch.dict(os.environ, {"USE_OPENAI_HEADLINE": "False"}):
        # Add logging to verify the environment variable
        print(f"USE_OPENAI_HEADLINE in test: {os.getenv('USE_OPENAI_HEADLINE')}")
        
        response = client.get("/extract-text", params={"url": url})
        assert response.status_code == 200
        assert response.json() == {"images": expected_images, "headlines": expected_headlines}
        for headline in response.json()["headlines"]:
            assert headline == "Ad headline"


def test_extract_text_bermuda():
    url = "https://thinkingofbermuda.com"
    
    with patch("app.routes.OpenAI", return_value=mock_openai_client()):
        with patch.dict(os.environ, {"USE_OPENAI_HEADLINE": "True"}):
            # Add logging to verify the environment variable
            print(f"USE_OPENAI_HEADLINE in test: {os.getenv('USE_OPENAI_HEADLINE')}")
            
            response = client.get("/extract-text", params={"url": url})
            assert response.status_code == 200
            assert "images" in response.json()
            assert "headlines" in response.json()
            for headline in response.json()["headlines"]:
                assert len(headline.split()) <= 5  # Ensure each headline is no more than 5 words

