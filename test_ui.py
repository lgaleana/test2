import pytest
from playwright.sync_api import sync_playwright
import json

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


def test_ui(browser):
    page = browser.new_page()

    # Mock the backend response
    mock_response = {
        "text": "Example Domain",
        "headlines": [
            {"image_url": "http://example.com/image1.jpg", "headline": "Sample Headline 1"},
            {"image_url": "http://example.com/image2.jpg", "headline": "Sample Headline 2"}
        ]
    }

    # Intercept the network request and return the mocked response
    def handle_route(route, request):
        if request.url.startswith("http://localhost:8080/extract-text"):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_response)
            )
        else:
            route.continue_()

    page.route("**/*", handle_route)

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Wait for the result to be updated
    page.wait_for_selector("#result", state="visible")
    page.wait_for_function("document.getElementById('result').textContent !== 'Loading...'")

    # Check the result
    result_text = page.text_content("#result")
    assert "Example Domain" in result_text

    # Check if images and headlines are displayed
    images = page.query_selector_all("img")
    headlines = page.query_selector_all("p")
    assert len(images) > 0
    assert len(headlines) > 0

    # Verify that each image has a corresponding headline
    for img, headline in zip(images, headlines):
        assert img.get_attribute("src") is not None
        assert headline.text_content() is not None
