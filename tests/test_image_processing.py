import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.image_processing import overlay_text_on_image
from io import BytesIO
import tempfile

client = TestClient(app)

@patch("app.image_processing.requests.get")
def test_overlay_text_on_image(mock_get):
    mock_response = MagicMock()
    # Use valid image bytes for the mock response content
    mock_response.content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
    mock_get.return_value = mock_response

    image_url = "http://example.com/image.jpg"
    text = "Sample Text"
    x, y = 10, 10

    result = overlay_text_on_image(image_url, text, x, y)
    assert result.endswith(".png")

@patch("app.routes.overlay_text_on_image")
def test_download_image(mock_overlay_text_on_image):
    # Create a temporary file to mock the overlayed image
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82')
        temp_file_path = temp_file.name

    mock_overlay_text_on_image.return_value = temp_file_path

    response = client.get("/download-image", params={
        "url": "http://example.com/image.jpg",
        "text": "Sample Text",
        "x": 10,
        "y": 10
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
