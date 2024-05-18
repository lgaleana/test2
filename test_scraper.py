import pytest
import requests
from scraper import extract_text_from_url

def test_extract_text_from_valid_url(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
        def raise_for_status(self):
            pass

    def mock_get(url):
        return MockResponse(b"<html><body><p>Hello, World!</p></body></html>")

    monkeypatch.setattr("requests.get", mock_get)
    text = extract_text_from_url("http://example.com")
    assert text == "Hello, World!"

def test_extract_text_from_invalid_url(monkeypatch):
    def mock_get(url):
        raise requests.RequestException("Invalid URL")

    monkeypatch.setattr("requests.get", mock_get)
    text = extract_text_from_url("http://invalid-url.com")
    assert text is None

def test_extract_text_from_url_with_no_text(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
        def raise_for_status(self):
            pass

    def mock_get(url):
        return MockResponse(b"<html><body></body></html>")

    monkeypatch.setattr("requests.get", mock_get)
    text = extract_text_from_url("http://example.com")
    assert text == ""
