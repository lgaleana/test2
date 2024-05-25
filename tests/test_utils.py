import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from app.scraping import extract_images
import requests
from PIL import Image
from io import BytesIO
import os  # Import the os module


def mock_requests_get(*args, **kwargs):
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    response = MagicMock()
    response.content = img_byte_arr.read()
    response.status_code = 200
    return response


@patch('requests.get', side_effect=mock_requests_get)
def test_extract_images_with_size_filter(mock_get):
    html_content = """
    <html>
        <body>
            <img src="http://example.com/image1.jpg" />
            <img src="http://example.com/image2.jpg" />
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with patch.dict(os.environ, {"MIN_IMAGE_WIDTH": "50", "MIN_IMAGE_HEIGHT": "50"}):
        expected_images = [
            "http://example.com/image1.jpg",
            "http://example.com/image2.jpg"
        ]
        assert extract_images(soup) == expected_images


@patch('requests.get', side_effect=mock_requests_get)
def test_extract_images_with_size_filter_exclude(mock_get):
    html_content = """
    <html>
        <body>
            <img src="http://example.com/image1.jpg" />
            <img src="http://example.com/image2.jpg" />
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with patch.dict(os.environ, {"MIN_IMAGE_WIDTH": "200", "MIN_IMAGE_HEIGHT": "200"}):
        expected_images = []
        assert extract_images(soup) == expected_images

