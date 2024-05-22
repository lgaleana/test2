import pytest


def test_ui_drag_and_drop_restriction(browser):
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
    page.wait_for_selector("#image-result .image-container")

    # Mock the bounding box data
    page.evaluate('''() => {
        document.querySelectorAll('.image-container').forEach(container => {
            container.getBoundingClientRect = () => ({ left: 0, top: 0, width: 500, height: 500 });
        });
        document.querySelectorAll('.draggable').forEach(draggable => {
            draggable.getBoundingClientRect = () => ({ left: 0, top: 0, width: 100, height: 50 });
        });
    }''')

    # Test drag-and-drop restriction
    for headline in page.query_selector_all("#image-result p.draggable"):
        box = headline.bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        page.mouse.down()
        page.mouse.move(box['x'] + 1000, box['y'] + 1000)  # Attempt to move outside the container
        page.mouse.up()
        new_box = headline.bounding_box()

        # Ensure the headline stays within the bounds of the container
        container_box = page.evaluate('''(headline) => {
            const container = headline.closest('.image-container');
            const rect = container.getBoundingClientRect();
            return { left: rect.left, top: rect.top, width: rect.width, height: rect.height };
        }''', headline)

        assert container_box['left'] <= new_box['x'] <= container_box['left'] + container_box['width'] - new_box['width']
        assert container_box['top'] <= new_box['y'] <= container_box['top'] + container_box['height'] - new_box['height']
