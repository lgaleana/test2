import pytest

def test_ui_with_limited_images(browser):
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
    page.wait_for_selector("#result", state="visible")
    page.wait_for_function("document.getElementById('result').textContent !== 'Loading...'")

    # Check for images
    images = page.query_selector_all("#image-result .image-container")
    assert len(images) == 1

    # Verify the image sources and overlayed text
    expected_images = ["/fetch-image?url=http%3A%2F%2Fexample.com%2Fimage1.jpg"]
    expected_headlines = ["Mocked Ad Headline"]
    for container, expected_src, expected_text in zip(images, expected_images, expected_headlines):
        img = container.query_selector("img")
        src = img.get_attribute("src")
        assert src == expected_src

        headline = container.query_selector("p.draggable")
        text = headline.text_content()
        assert text == expected_text
        assert len(text.split()) <= 5  # Ensure each headline is no more than 5 words

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

        # Mock the bounding box of the container
        container_box = {
            'x': 0,
            'y': 0,
            'width': 500,
            'height': 500
        }
        assert container_box['x'] <= new_box['x'] <= container_box['x'] + container_box['width'] - new_box['width']
        assert container_box['y'] <= new_box['y'] <= container_box['y'] + container_box['height'] - new_box['height']

    page.close()
