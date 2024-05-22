from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import os
from app.scraping import extract_images
from app.openai_utils import generate_headline
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import io

# Load environment variables
load_dotenv()

# Initialize OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

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

@app.post("/download-image")
def download_image(request: DownloadImageRequest):
    response = requests.get(request.image_url)
    image = Image.open(io.BytesIO(response.content))

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text_position = (10, 10)  # Example position, you might want to make this dynamic
    draw.text(text_position, request.text, font=font, fill="black")

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return FileResponse(output, media_type="image/png", filename="image_with_text.png")
