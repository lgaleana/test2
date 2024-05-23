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

    # Mock the download image request
    page.route("**/download-image?**", lambda route: route.fulfill(
        status=200,
        content_type="image/png",
        body="mocked_image_content"
    ))

    # Ensure the "Download" button is clickable
    page.wait_for_selector("button:has-text('Download')")

    # Click the download button
    with page.expect_download() as download_info:
        page.click("button:has-text('Download')")
    download = download_info.value

    # Verify the download
    path = download.path()
    assert path is not None
