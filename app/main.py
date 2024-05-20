from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl
import requests
from bs4 import BeautifulSoup
import os

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

    # Extract images
    images = []
    for img in soup.find_all("img"):
        if img.get("src"):
            images.append(img["src"])
    for tag in soup.find_all(style=True):
        style = tag["style"]
        if "background-image" in style:
            start = style.find("url(") + 4
            end = style.find(")", start)
            images.append(style[start:end].strip('"').strip("'"))
    for meta in soup.find_all("meta", property="og:image"):
        if meta.get("content"):
            images.append(meta["content"])

    return {"text": text, "images": images}
