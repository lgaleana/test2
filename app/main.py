from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import HttpUrl
import requests
from bs4 import BeautifulSoup
import os

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open(os.path.join("templates", "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/extract-text")
def extract_text(url: HttpUrl = Query(..., description="The URL to extract text from")):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return {"text": text}
