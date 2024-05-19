from fastapi import FastAPI, HTTPException, Query
from bs4 import BeautifulSoup
import requests

app = FastAPI()

@app.get("/extract-text")
def extract_text(url: str = Query(..., description="The URL to scrape text from")):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return {"text": text}
