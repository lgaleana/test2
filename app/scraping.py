from bs4 import BeautifulSoup
import os
import requests
from PIL import Image
from io import BytesIO
import logging

# Define global variables for minimum image dimensions
MIN_IMAGE_WIDTH = int(os.getenv("MIN_IMAGE_WIDTH", 300))
MIN_IMAGE_HEIGHT = int(os.getenv("MIN_IMAGE_HEIGHT", 250))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_images(soup: BeautifulSoup) -> list:
    images = []
    n_images = int(os.getenv("N_IMAGES", 4))  # Default to 4 if not set

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    for img in soup.find_all(["img", "meta", "link", "source"]):
        img_url = None
        if img.name == "img" and img.get("src"):
            img_url = img["src"]
        elif img.name == "meta" and img.get("content") and "image" in img.get("property", ""):
            img_url = img["content"]
        elif img.name == "link" and img.get("href") and "image" in img.get("type", ""):
            img_url = img["href"]
        elif img.name == "source" and img.get("srcset"):
            img_url = img["srcset"].split()[0]  # Take the first URL in srcset

        if img_url:
            try:
                response = requests.get(img_url, headers=headers)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                if image.width >= MIN_IMAGE_WIDTH and image.height >= MIN_IMAGE_HEIGHT:
                    images.append(img_url)
            except requests.RequestException as e:
                logger.error(f"RequestException for URL {img_url}: {e}")
                continue
            except IOError as e:
                logger.error(f"IOError for URL {img_url}: {e}")
                continue

        if len(images) >= n_images:
            break

    return images
