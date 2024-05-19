from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests

app = FastAPI()

class URLRequest(BaseModel):
    url: str

@app.post("/extract-text")
async def extract_text(request: URLRequest):
    try:
        response = requests.get(request.url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return {"text": text}
