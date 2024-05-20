import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


def test_ui(browser):
    page = browser.new_page()

    # Mock the fetch request to /extract-text
    page.route("**/extract-text?url=http%3A%2F%2Fexample.com", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"text": "Example Domain", "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"], "headlines": ["Mocked Ad Headline", "Another Mocked Headline"]}'
    ))

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Wait for the result to be updated
    page.wait_for_selector("#result", state="visible")
    page.wait_for_function("document.getElementById('result').textContent !== 'Loading...'")

    # Check the result
    result_text = page.text_content("#text-result")
    assert "Example Domain" in result_text

    # Check for images
    images = page.query_selector_all("#image-result img")
    assert len(images) == 2

    # Verify the image sources
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    for img, expected_src in zip(images, expected_images):
        src = img.get_attribute("src")
        assert src == expected_src

    # Verify the headlines
    headlines = page.query_selector_all("#image-result p")
    expected_headlines = ["Mocked Ad Headline", "Another Mocked Headline"]
    for headline, expected_text in zip(headlines, expected_headlines):
        text = headline.text_content()
        assert text == expected_text
        assert len(text.split()) <= 5  # Ensure each headline is no more than 5 words


def test_ui_with_limited_images(browser):
    page = browser.new_page()

    # Mock the fetch request to /extract-text
    page.route("**/extract-text?url=http%3A%2F%2Fexample.com", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"text": "Example Domain", "images": ["http://example.com/image1.jpg"], "headlines": ["Mocked Ad Headline"]}'
    ))

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Wait for the result to be updated
    page.wait_for_selector("#result", state="visible")
    page.wait_for_function("document.getElementById('result').textContent !== 'Loading...'")

    # Check the result
    result_text = page.text_content("#text-result")
    assert "Example Domain" in result_text

    # Check for images
    images = page.query_selector_all("#image-result img")
    assert len(images) == 1

    # Verify the image sources
    expected_images = ["http://example.com/image1.jpg"]
    for img, expected_src in zip(images, expected_images):
        src = img.get_attribute("src")
        assert src == expected_src

    # Verify the headlines
    headlines = page.query_selector_all("#image-result p")
    expected_headlines = ["Mocked Ad Headline"]
    for headline, expected_text in zip(headlines, expected_headlines):
        text = headline.text_content()
        assert text == expected_text
        assert len(text.split()) <= 5  # Ensure each headline is no more than 5 words
