import pytest

def test_ui_drag_and_drop_functionality(browser):
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

    # Test drag-and-drop functionality
    for headline in page.query_selector_all("#image-result p.draggable"):
        box = headline.bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        page.mouse.down()
        page.mouse.move(box['x'] + 100, box['y'] + 100)
        page.mouse.up()
        new_box = headline.bounding_box()
        assert new_box['x'] != box['x'] or new_box['y'] != box['y']  # Ensure the position has changed
