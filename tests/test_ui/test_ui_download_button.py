import pytest

@pytest.mark.usefixtures("server")
def test_ui_download_button(browser):
    page = browser.new_page()

    # Mock the fetch request to /extract-text
    page.route("**/extract-text?url=http%3A%2F%2Fexample.com", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"], "headlines": ["Mocked Ad Headline", "Another Mocked Headline"]}'
    ))

    # Mock the fetch request to /download-image
    page.route("**/download-image", lambda route: route.fulfill(
        status=200,
        content_type="image/png",
        body=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xff\xa0\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0bIDATx\xdacddbf\xa0\x040Q\xa4\x00\x00\x00\x00IEND\xaeB`\x82'
    ))

    page.goto("http://localhost:8080/")

    # Test form submission
    page.fill("input[name='url']", "http://example.com")
    page.click("button[type='submit']")

    # Wait for the result to be updated
    page.wait_for_selector("#image-result .image-container")

    # Check for download buttons
    download_buttons = page.query_selector_all(".download-button")
    assert len(download_buttons) == 2

    # Click the download button and verify the download
    with page.expect_download() as download_info:
        download_buttons[0].click()
    download = download_info.value
    assert download.suggested_filename == "overlayed_image.png"
