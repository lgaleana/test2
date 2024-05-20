from bs4 import BeautifulSoup
import os


def extract_images(soup: BeautifulSoup) -> list:
    images = []
    n_images = int(os.getenv("N_IMAGES", 4))  # Default to 4 if not set
    for img in soup.find_all(["img", "meta", "link", "source"]):
        if img.name == "img" and img.get("src"):
            images.append(img["src"])
        elif img.name == "meta" and img.get("content") and "image" in img.get("property", ""):
            images.append(img["content"])
        elif img.name == "link" and img.get("href") and "image" in img.get("type", ""):
            images.append(img["href"])
        elif img.name == "source" and img.get("srcset"):
            images.append(img["srcset"].split()[0])  # Take the first URL in srcset
        if len(images) >= n_images:
            break
    return images
