import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the backend folder to python path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture(scope="module")
def client():
    # Create a test client
    with TestClient(app) as c:
        yield c