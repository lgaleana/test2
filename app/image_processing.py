from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import tempfile

def overlay_text_on_image(image_url: str, text: str, x: int, y: int) -> str:
    response = requests.get(image_url)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((x, y), text, font=font, fill="black")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image.save(temp_file, format="PNG")
    temp_file.close()

    return temp_file.name
