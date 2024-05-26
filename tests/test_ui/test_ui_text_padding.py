import pytest

def test_ui_text_padding(browser):
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

    # Verify the absence of padding
    headline = page.query_selector("#image-result p.draggable")
    padding = page.evaluate('''(headline) => {
        return window.getComputedStyle(headline).padding;
    }''', headline)
    
    # Log the padding value for debugging
    print(f"Computed padding: {padding}")
    
    assert padding == "0px"  # Ensure no padding

    page.close()
