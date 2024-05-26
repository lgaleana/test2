import pytest

def test_ui_text_color(browser):
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

    # Change the text color
    color_input = page.query_selector("#image-result .image-container input[type='color']")
    color_input.fill("#FF0000")  # Set color to red

    # Verify the text color in the UI
    headline = page.query_selector("#image-result p.draggable")
    color = page.evaluate('''(headline) => {
        return window.getComputedStyle(headline).color;
    }''', headline)
    assert color == "rgb(255, 0, 0)"  # Ensure the color is red

    # Mock the download request
    page.route("**/download-image", lambda route: route.fulfill(
        status=200,
        content_type="image/png",
        headers={"Content-Disposition": "attachment; filename=overlayed_image.png"},
        body=b""
    ))

    # Click the download button for the first image
    with page.expect_download() as download_info:
        page.click("#image-result .image-container:nth-of-type(1) button:nth-of-type(2)")  # Ensure the correct button is clicked
    download = download_info.value

    # Verify the download
    assert download.suggested_filename == "overlayed_image.png"

    page.close()
