import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from io import BytesIO

client = TestClient(app)

def mock_requests_get(*args, **kwargs):
    img_byte_arr = BytesIO(b"fake image content")
    response = MagicMock()
    response.content = img_byte_arr.read()
    response.status_code = 200
    response.headers = {'Content-Type': 'image/png'}
    return response

@patch('requests.get', side_effect=mock_requests_get)
def test_fetch_image(mock_get):
    response = client.get("/fetch-image", params={"url": "http://example.com/image.png"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.content == b"fake image content"
