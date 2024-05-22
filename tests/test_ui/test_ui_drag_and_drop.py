import pytest


def test_ui_drag_and_drop(browser):
    page = browser.new_page()

    # Mock the fetch request to /extract-text
    page.route("**/extract-text?url=http%3A%2F%2Fexample.com", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"], "headlines": ["Mocked Ad Headline", "Another Mocked Headline"]}'
    ))

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Wait for the result to be updated
    page.wait_for_selector("#result", state="visible")
    page.wait_for_function("document.getElementById('result').textContent !== 'Loading...'")

    # Test drag-and-drop functionality
    for headline in page.query_selector_all("#image-result p.draggable"):
        box = headline.bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        page.mouse.down()
        page.mouse.move(box['x'] + 100, box['y'] + 100)
        page.mouse.up()
        new_box = headline.bounding_box()
        assert new_box['x'] != box['x'] or new_box['y'] != box['y']  # Ensure the position has changed

        # Mock the bounding box of the container
        container_box = {
            'x': 0,
            'y': 0,
            'width': 500,
            'height': 500
        }
        assert container_box['x'] <= new_box['x'] <= container_box['x'] + container_box['width'] - new_box['width']
        assert container_box['y'] <= new_box['y'] <= container_box['y'] + container_box['height'] - new_box['height']
