import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from io import BytesIO
from PIL import Image, ImageFont

client = TestClient(app)


def mock_requests_get(*args, **kwargs):
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    response = MagicMock()
    response.content = img_byte_arr.read()
    response.status_code = 200
    return response


@patch('requests.get', side_effect=mock_requests_get)
@patch('PIL.ImageFont.truetype')
def test_download_image(mock_truetype, mock_get):
    # Mock the font loading to avoid dependency on the actual font file
    mock_truetype.return_value = ImageFont.load_default()

    response = client.post("/download-image", json={"image_url": "http://example.com/image.png", "text": "Test", "x": 10, "y": 10})
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=overlayed_image.png"
    assert response.headers["Content-Type"] == "image/png"
