import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from app.scraping import extract_images
from io import BytesIO
from PIL import Image
import os


def mock_requests_get_image(*args, **kwargs):
    url = str(args[0])  # Convert the URL to a string
    if url.startswith("http://example.com/image"):
        img = Image.new('RGB', (300, 250), color=(73, 109, 137))  # Ensure the image meets the size criteria
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

@patch('requests.get', side_effect=mock_requests_get_image)
def test_extract_images_with_allowed_sizes(mock_get):
    html_content = """
    <html>
        <body>
            <img src="http://example.com/image1.jpg" />
            <img src="http://example.com/image2.jpg" />
        </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with patch.dict(os.environ, {"ALLOWED_IMAGE_SIZES": "300x250,728x90,160x600,300x600"}):
        expected_images = [
            "http://example.com/image1.jpg",
            "http://example.com/image2.jpg"
        ]
        assert extract_images(soup) == expected_images


def mock_requests_get_small_image(*args, **kwargs):
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))  # Ensure the image does not meet the size criteria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    response = MagicMock()
    response.content = img_byte_arr.read()
    response.status_code = 200
    return response

@patch('requests.get', side_effect=mock_requests_get_small_image)
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
    with patch.dict(os.environ, {"ALLOWED_IMAGE_SIZES": "300x250,728x90,160x600,300x600"}):  # Ensure the size criteria exclude the images
        expected_images = []
        assert extract_images(soup) == expected_images
