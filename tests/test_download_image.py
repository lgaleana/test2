import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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
def test_download_image(mock_get):
    # Create a mock image file
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    files = {'image': ('image.png', img_byte_arr, 'image/png')}
    data = {
        'text': 'Test', 
        'x': 10, 
        'y': 10, 
        'font_size': 20, 
        'color': '#FF0000', 
        'font_type': 'Arial',
        'headline': 'Test_Headline'  # Include headline in the data
    }

    response = client.post("/download-image", files=files, data=data)
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=Test_Headline.png"
    assert response.headers["Content-Type"] == "image/png"

    # Verify the image content
    img = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(img)
    font_path = "app/static/fonts/Arial.ttf"
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)
    text_bbox = draw.textbbox((10, 10), "Test", font=font)
    assert text_bbox is not None

    # Verify the text color
    pixel_color = img.getpixel((text_bbox[0] + 1, text_bbox[1] + 1))  # Get the color of a pixel within the text bounding box
    assert pixel_color == (255, 0, 0)  # Ensure the color is red (#FF0000)
