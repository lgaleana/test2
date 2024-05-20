import pytest
from unittest.mock import patch, MagicMock
import os


def mock_openai_chat_completion_create(*args, **kwargs):
    class MockResponse:
        def __init__(self):
            self.choices = [self]

        @property
        def message(self):
            class Message:
                def __init__(self):
                    self.content = "Mocked Ad Headline"
            return Message()

    return MockResponse()


@pytest.fixture(autouse=True)
def set_openai_api_key():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
        yield


def mock_openai_client():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mock_openai_chat_completion_create
    return mock_client
