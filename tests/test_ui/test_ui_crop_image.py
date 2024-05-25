import pytest

def test_ui_crop_image(browser):
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

    # Click the crop button
    page.click("#image-result .image-container button:nth-of-type(1)")

    # Wait for the crop container to be visible
    page.wait_for_selector("#crop-container", state="visible")

    # Perform cropping action
    page.click("#crop-button")

    # Verify the cropped image
    crop_image = page.query_selector("#crop-image")
    assert crop_image is not None

    page.close()
