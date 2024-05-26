import pytest

def test_ui_text_editing(browser):
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

    # Add a small delay to ensure all elements are rendered and positioned
    page.wait_for_timeout(1000)

    # Edit the text
    headline = page.query_selector("#image-result p.draggable")
    headline.click()
    page.keyboard.press("Control+A")
    page.keyboard.type("Edited Headline")
    page.keyboard.press("Enter")

    # Verify the edited text
    edited_text = headline.text_content()
    assert edited_text == "Edited Headline"

    page.close()
