
import pytest
from fastapi.testclient import TestClient
from main import app, CSV_FILE
import os
import tempfile

# Create a TestClient
client = TestClient(app)

@pytest.fixture
def setup_csv():
    # Create a temporary file
    temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_csv.close()  # Close so the file can be used elsewhere

    # Add test data that matches the parameters in test_generate_mcq
    data = (
        "question,subject,use,correct,responseA,responseB,responseC,responseD,remark\n"
        "What is BDD?,BDD,Test de positionnement,A,Business Development,Business Data Design,Business Driven Development,,\n"
    )
    with open(temp_csv.name, "w") as f:
        f.write(data)

    # Override the CSV_FILE variable in the main module
    global CSV_FILE
    original_csv_file = CSV_FILE
    CSV_FILE = temp_csv.name

    yield  # Test cases will run here

    # Cleanup: Delete the temporary file and restore the original CSV_FILE path
    os.remove(temp_csv.name)
    CSV_FILE = original_csv_file


    
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
    response = client.get("/questions/", auth=("alice", "wonderland"))
    assert response.status_code == 403


# Tests go here, using the setup_csv fixture
def test_get_questions_admin(setup_csv):
    response = client.get("/questions/", auth=("admin", "4dm1N"))
    assert response.status_code == 200
    assert len(response.json()) > 0


# Test fetching questions by subject
def test_get_questions_by_subject(setup_csv):
    response = client.get("/questions/subject/BDD", auth=("admin", "4dm1N"))
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) > 0
    assert questions[0]["subject"] == "BDD"
    
# Create question
def test_create_question(setup_csv):
    new_question = {
        "question": "Test",
        "subject": "API",
        "use": "Total Bootcamp",
        "correct": "Test",
        "responseA": "Python",
        "responseB": "Java",
        "responseC": "Ruby",
        "responseD": "None",
    }
    response = client.post("/questions/", json=new_question, auth=("admin", "4dm1N"))
    assert response.status_code == 200
    assert response.json()["message"] == "Question added successfully!"
    assert response.json()["question"]["question"] == "Test"
    
    
def test_generate_mcq(setup_csv):
    params = {"subjects": ["BDD"], "use": "Test de positionnement", "num_questions": 5}
    response = client.get("/generate-mcq/", params=params)
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert response.json()[0]["subject"] == "BDD"
    assert response.json()[0]["use"] == "Test de positionnement"


# Test invalid number of questions for MCQ generation
def test_generate_mcq_invalid_num_questions():
    params = {"subjects": ["BDD"], "use": "Test de positionnement", "num_questions": 3}
    response = client.get("/generate-mcq/", params=params)
    assert response.status_code == 400
    assert response.json()["detail"] == "Number of questions must be 5, 10, or 20."
    


# tests/test_main.py 

