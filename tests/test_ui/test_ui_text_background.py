import pytest

def test_ui_text_background(browser):
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

    # Verify the absence of background color
    headline = page.query_selector("#image-result p.draggable")
    background_color = page.evaluate('''(headline) => {
        return window.getComputedStyle(headline).backgroundColor;
    }''', headline)
    assert background_color == "rgba(0, 0, 0, 0)"  # Transparent background

    page.close()
