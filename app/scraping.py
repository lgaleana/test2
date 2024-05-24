from bs4 import BeautifulSoup
import os
import requests
from PIL import Image
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global variables for minimum width and height
MIN_IMAGE_WIDTH = 300
MIN_IMAGE_HEIGHT = 250

def extract_images(soup: BeautifulSoup) -> list:
    images = []
    n_images = int(os.getenv("N_IMAGES", 4))  # Default to 4 if not set

    for img in soup.find_all(["img", "meta", "link", "source"]):
        if img.name == "img" and img.get("src"):
            image_url = img["src"]
        elif img.name == "meta" and img.get("content") and "image" in img.get("property", ""):
            image_url = img["content"]
        elif img.name == "link" and img.get("href") and "image" in img.get("type", ""):
            image_url = img["href"]
        elif img.name == "source" and img.get("srcset"):
            image_url = img["srcset"].split()[0]  # Take the first URL in srcset
        else:
            continue

        # Check image dimensions
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            width, height = image.size
            logging.info(f"Image URL: {image_url}, Width: {width}, Height: {height}")
            if width >= MIN_IMAGE_WIDTH and height >= MIN_IMAGE_HEIGHT:
                images.append(image_url)
        except requests.RequestException as e:
            logging.error(f"RequestException for URL {image_url}: {e}")
            continue
        except Exception as e:
            logging.error(f"Exception for URL {image_url}: {e}")
            continue

        if len(images) >= n_images:
            break

    return images
