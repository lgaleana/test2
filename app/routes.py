from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from app.templates import templates
from app.scraping import extract_images
from app.openai_utils import generate_headline
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import HttpUrl, BaseModel
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

class DownloadImageRequest(BaseModel):
    image_url: HttpUrl
    text: str
    x: int
    y: int

@app.post("/download-image")
def download_image(request: DownloadImageRequest):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "*/*",
    }
    try:
        response = requests.get(request.image_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    image = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # You can specify a custom font here

    draw.text((request.x, request.y), request.text, font=font, fill="black")

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png", headers={"Content-Disposition": "attachment; filename=overlayed_image.png"})
