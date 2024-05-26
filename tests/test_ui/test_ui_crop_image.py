import pytest
from io import BytesIO
from PIL import Image

def test_ui_crop_image(browser):
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

    # Wait for the result to be updated
    page.wait_for_selector("#image-result .image-container")

    # Click the crop button
    page.click("#image-result .image-container button:nth-of-type(1)")

    # Wait for the crop container to be visible
    page.wait_for_selector("#crop-container", state="visible")

    # Perform cropping action
    page.click("#crop-button")

    # Verify the cropped image
    crop_image = page.query_selector("#image-result .image-container img")
    assert crop_image is not None

    # Ensure the original images are still present
    original_images = page.query_selector_all("#image-result .image-container img")
    assert len(original_images) == 1  # Ensure only one image is present

    # Test drag-and-drop functionality on the cropped image
    headline = page.query_selector("#image-result p.draggable")
    box = headline.bounding_box()
    print(f"Initial position: x={box['x']}, y={box['y']}")  # Log initial position
    page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    page.mouse.down()
    page.mouse.move(box['x'] + 100, box['y'] + 100)
    page.mouse.up()
    new_box = headline.bounding_box()
    print(f"New position: x={new_box['x']}, y={new_box['y']}")  # Log new position
    assert new_box['x'] != box['x'] or new_box['y'] != box['y']  # Ensure the position has changed

    # Mock the download request
    page.route("**/download-image", lambda route: route.fulfill(
        status=200,
        content_type="image/png",
        headers={"Content-Disposition": "attachment; filename=overlayed_image.png"},
        body=b""
    ))

    # Click the download button for the cropped image
    with page.expect_download() as download_info:
        page.click("#image-result .image-container button:nth-of-type(2)")  # Ensure the correct button is clicked
    download = download_info.value

    # Verify the download
    assert download.suggested_filename == "overlayed_image.png"

    page.close()
