import pytest

def test_ui_download_image(browser):
    page = browser.new_page()

    # Mock the fetch request to /extract-text
    page.route("**/extract-text?url=http%3A%2F%2Fexample.com", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"images": ["http://example.com/image1.jpg"], "headlines": ["Mocked Ad Headline"]}'
    ))

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Wait for the result to be updated
    page.wait_for_selector("#image-result .image-container")

    # Ensure the download button is clickable
    page.wait_for_selector(".download-button", state="visible")

    # Click the download button
    page.click(".download-button")

    # Verify the download (this is a bit tricky to test directly, but we can check for the request)
    download_request = page.wait_for_request("**/download-image")
    assert download_request is not None
    assert download_request.method == "POST"
    assert download_request.post_data_json() == {
        "image_url": "http://example.com/image1.jpg",
        "text": "Mocked Ad Headline",
        "x": 0,
        "y": 0
    }
