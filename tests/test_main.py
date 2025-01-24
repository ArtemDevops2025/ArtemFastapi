import pytest
from fastapi.testclient import TestClient
from main import app, users, CSV_FILE
import os

# Create a TestClient
client = TestClient(app)

# Fixtures
@pytest.fixture
def setup_csv():
    
    if not os.path.exists(CSV_FILE):
        data = (
            "question,subject,use,correct,responseA,responseB,responseC,responseD,remark\n"
            "What is BDD?,BDD,Test de positionnement,A,Business Development,Business Data Design,Business Driven Development,,\n"
        )
        with open(CSV_FILE, "w") as f:
            f.write(data)
    yield
    os.remove(CSV_FILE)

# Test root endpoint
def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "There is no application here!"}

# Test health check
def test_verify():
    response = client.get("/verify")
    assert response.status_code == 200
    assert response.json() == {"message": "I'm ok! Welcome!"}
    
# Test authentication
def test_authenticate_user():
    # Correct credentials
    response = client.get("/questions/", auth=("admin", "4dm1N"))
    assert response.status_code == 200

    # Incorrect credentials
    response = client.get("/questions/", auth=("admin", "wrongpassword"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}