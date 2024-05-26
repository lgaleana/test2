from fastapi import APIRouter, HTTPException, Query, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from app.templates import templates
from app.scraping import extract_images
from app.openai_utils import generate_headline
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import HttpUrl, BaseModel, Field
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()

# Initialize OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

app = APIRouter()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/extract-text")
def extract_text(url: HttpUrl = Query(..., description="The URL to extract text and images from")):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    text = "\n".join([line for line in text.split("\n") if line.strip()])  # Remove empty lines

    # Extract images using the utility method
    images = extract_images(soup)

    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Generate headlines for each image
    headlines = [generate_headline(client, text, image) for image in images]

    return {"images": images, "headlines": headlines}

@app.post("/download-image")
async def download_image(
    image: UploadFile = File(...), 
    text: str = Form(...), 
    x: float = Form(...), 
    y: float = Form(...),
    font_size: int = Form(...)
):
    try:
        image_data = await image.read()
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    draw = ImageDraw.Draw(image)
    
    # Load a TrueType font
    font_path = "app/static/fonts/Arial.ttf"
    font = ImageFont.truetype(font_path, font_size)  # Use the provided font size

    # Adjust the coordinates to account for any transformations or scaling
    adjusted_x = int(x)
    adjusted_y = int(y)

    # Apply any necessary adjustments to the coordinates
    # For example, if the y-coordinate is off, adjust it here
    adjusted_y += 10  # Adjust the y-coordinate by 10 pixels (example adjustment)

    draw.text((adjusted_x, adjusted_y), text, font=font, fill="black")

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png", headers={"Content-Disposition": "attachment; filename=overlayed_image.png"})

@app.get("/fetch-image")
def fetch_image(url: HttpUrl):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(BytesIO(response.content), media_type=response.headers['Content-Type'])
