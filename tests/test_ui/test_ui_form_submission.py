import pytest


def test_ui_form_submission(browser):
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

    # Check for images
    images = page.query_selector_all("#image-result .image-container")
    assert len(images) == 2

    # Verify the image sources and overlayed text
    expected_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    expected_headlines = ["Mocked Ad Headline", "Another Mocked Headline"]
    for container, expected_src, expected_text in zip(images, expected_images, expected_headlines):
        img = container.query_selector("img")
        src = img.get_attribute("src")
        assert src == expected_src

        headline = container.query_selector("p.draggable")
        text = headline.text_content()
        assert text == expected_text
        assert len(text.split()) <= 5  # Ensure each headline is no more than 5 words
