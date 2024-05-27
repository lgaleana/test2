import pytest
from io import BytesIO
from PIL import Image


def test_ui_loading_indicator(browser):
    page = browser.new_page()

    # Mock the fetch request to /extract-text
    page.route("**/extract-text?url=http%3A%2F%2Fexample.com", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"images": ["http://example.com/image1.jpg"], "headlines": ["Mocked Ad Headline"]}'
    ))

    # Mock the fetch request to /fetch-image
    def mock_fetch_image(route):
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        route.fulfill(
            status=200,
            content_type="image/png",
            body=img_byte_arr.read()
        )

    page.route("**/fetch-image?url=http%3A%2F%2Fexample.com%2Fimage1.jpg", mock_fetch_image)

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Log the state of the loading indicator before waiting
    loading_indicator = page.query_selector("#loading-indicator")
    print(f"Loading indicator visible before wait: {loading_indicator.is_visible()}")

    # Wait for the loading indicator to appear
    page.wait_for_selector("#loading-indicator", state="visible")

    # Verify the loading indicator is visible
    assert loading_indicator.is_visible()

    # Wait for the result to be updated
    page.wait_for_selector("#image-result .image-container")

    # Verify the loading indicator is hidden
    assert not loading_indicator.is_visible()

    page.close()
