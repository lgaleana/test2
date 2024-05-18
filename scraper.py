import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    """
    Extracts all text from the given URL.

    Args:
        url (str): The URL to scrape.

    Returns:
        str: The extracted text, or None if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        return text
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")
    text = extract_text_from_url(url)
    if text:
        print(text)
