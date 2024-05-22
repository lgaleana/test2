from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from app.templates import templates
from app.scraping import extract_images
from app.openai_utils import generate_headline
from app.image_processing import overlay_text_on_image
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import HttpUrl
import requests
from bs4 import BeautifulSoup
import tempfile

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

@app.get("/download-image", response_class=FileResponse)
def download_image(url: HttpUrl, text: str, x: int, y: int):
    try:
        image_path = overlay_text_on_image(url, text, x, y)
        return FileResponse(image_path, media_type="image/png", filename="overlayed_image.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
