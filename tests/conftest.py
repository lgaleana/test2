import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def server(client):
    import subprocess
    import time

    # Start the FastAPI server
    process = subprocess.Popen(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"])
    time.sleep(2)  # Give the server a moment to start

    yield

    # Terminate the server after tests
    process.terminate()
