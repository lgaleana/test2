import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from app.scraping import extract_images
from io import BytesIO
from PIL import Image


def mock_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            pass

    if args[0] == "http://example.com/image1.jpg":
        img = Image.new('RGB', (150, 150), color = (73, 109, 137))
    else:
        img = Image.new('RGB', (50, 50), color = (73, 109, 137))
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return MockResponse(img_byte_arr.read())


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
    expected_images = ["http://example.com/image1.jpg"]
    assert extract_images(soup) == expected_images
