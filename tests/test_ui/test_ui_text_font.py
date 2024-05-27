import pytest

def test_ui_text_font(browser):
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

    # Change the font type using evaluate
    font_type_input = page.query_selector("#image-result .image-container select[name='font-type']")
    page.evaluate('(font_type_input) => { font_type_input.value = "Courier_New"; font_type_input.dispatchEvent(new Event("change")); }', font_type_input)  # Set font to Courier New and trigger change event

    # Verify the text font in the UI
    headline = page.query_selector("#image-result p.draggable")
    font_family = page.evaluate('''(headline) => {
        return window.getComputedStyle(headline).fontFamily;
    }''', headline)

    # Log the font family for debugging
    print(f"Font family: {font_family}")

    # Strip quotes and compare
    assert font_family.strip('"') == "Courier New"  # Ensure the font is Courier New

    # Mock the download request
    page.route("**/download-image", lambda route: route.fulfill(
        status=200,
        content_type="image/png",
        headers={"Content-Disposition": "attachment; filename=Mocked_Ad_Headline.png"},
        body=b""
    ))

    # Click the download button for the first image
    with page.expect_download() as download_info:
        page.click("#image-result .image-container:nth-of-type(1) button:nth-of-type(2)")  # Ensure the correct button is clicked
    download = download_info.value

    # Verify the download
    assert download.suggested_filename == "Mocked_Ad_Headline.png"

    page.close()
