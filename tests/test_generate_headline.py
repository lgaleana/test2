import pytest
from unittest.mock import patch
from app.openai_utils import generate_headline
from tests.mock_utils import mock_openai_client

def test_generate_headline():
    text = "This is a sample website text."
    image_url = "http://example.com/image.jpg"
    mock_client = mock_openai_client()
    headline = generate_headline(mock_client, text, image_url)
    assert headline == "Mocked Ad Headline"
    assert len(headline.split()) <= 5  # Ensure the headline is no more than 5 words
