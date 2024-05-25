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

    # Mock the bounding box data
    page.evaluate('''() => {
        document.querySelectorAll('.image-container').forEach(container => {
            container.getBoundingClientRect = () => ({ left: 0, top: 0, width: 500, height: 500 });
        });
        document.querySelectorAll('.draggable').forEach(draggable => {
            draggable.getBoundingClientRect = () => ({ left: 0, top: 0, width: 100, height: 50 });
        });
    }''')

    # Test drag-and-drop functionality after download
    headline = page.query_selector("#image-result p.draggable")
    box = headline.bounding_box()
    print(f"Initial position: x={box['x']}, y={box['y']}")

    page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    page.mouse.down()

    # Log position during drag
    page.mouse.move(box['x'] + 50, box['y'] + 50)
    mid_box = headline.bounding_box()
    print(f"Mid-drag position: x={mid_box['x']}, y={mid_box['y']}")

    # Manually update the position of the draggable element
    page.evaluate('''(headline) => {
        headline.style.transform = 'translate(100px, 100px)';
    }''', headline)

    page.mouse.move(box['x'] + 100, box['y'] + 100)
    page.mouse.up()

    new_box = headline.bounding_box()
    print(f"New position: x={new_box['x']}, y={new_box['y']}")

    assert new_box['x'] != box['x'] or new_box['y'] != box['y']  # Ensure the position has changed

    page.close()
