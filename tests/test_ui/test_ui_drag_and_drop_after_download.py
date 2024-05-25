import pytest

def test_ui_drag_and_drop_after_download(browser):
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

    # Mock the download request
    page.route("**/download-image", lambda route: route.fulfill(
        status=200,
        content_type="image/png",
        headers={"Content-Disposition": "attachment; filename=overlayed_image.png"},
        body=b""
    ))

    # Click the download button
    page.click("#image-result .image-container button")

    # Verify the download
    download = page.wait_for_event("download")
    assert download.suggested_filename == "overlayed_image.png"

    # Test drag-and-drop functionality after download
    headline = page.query_selector("#image-result p.draggable")
    box = headline.bounding_box()
    page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    page.mouse.down()
    page.mouse.move(box['x'] + 100, box['y'] + 100)
    page.mouse.up()
    new_box = headline.bounding_box()

    assert new_box['x'] != box['x'] or new_box['y'] != box['y']  # Ensure the position has changed

    page.close()
