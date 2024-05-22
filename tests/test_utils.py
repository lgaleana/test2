import pytest
from unittest.mock import patch
import os
from bs4 import BeautifulSoup
from app.openai_utils import generate_headline
from app.scraping import extract_images
from tests.mock_utils import mock_openai_client


def test_generate_headline():
    text = "This is a sample website text."
    image_url = "http://example.com/image.jpg"
    mock_client = mock_openai_client()
    headline = generate_headline(mock_client, text, image_url)
    assert headline == "Mocked Ad Headline"
    assert len(headline.split()) <= 5  # Ensure the headline is no more than 5 words


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

