from bs4 import BeautifulSoup

def extract_images(soup: BeautifulSoup) -> list:
    images = []
    for img in soup.find_all(["img", "meta", "link", "source"]):
        if img.name == "img" and img.get("src"):
            images.append(img["src"])
        elif img.name == "meta" and img.get("content") and "image" in img.get("property", ""):
            images.append(img["content"])
        elif img.name == "link" and img.get("href") and "image" in img.get("type", ""):
            images.append(img["href"])
        elif img.name == "source" and img.get("srcset"):
            images.append(img["srcset"].split()[0])  # Take the first URL in srcset
    return images
