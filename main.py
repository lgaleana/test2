from fastapi import FastAPI, HTTPException, Query
from pydantic import HttpUrl
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/extract-text")
def extract_text(url: HttpUrl = Query(..., description="The URL to scrape text from")):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    print(text)  # Print the scraped text
    return {"text": text}
