from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import os



app = FastAPI(
    title="Exam API",
    description="This API powered by FastAPI.",
    version="1.0.1",
    app_tags=[
        {"name": "health ", "description": "health check"},
        {"name": "Admin Tasks", "description": "Only for admin"},
        {"name": "Users Task", "description": "User get random quiz"},
    ],
)
# --------------Load the CSV file
CSV_FILE = "questions.csv"
if not os.path.exists(CSV_FILE):
    raise Exception(f"CSV file '{CSV_FILE}' not found.")

df = pd.read_csv(CSV_FILE, encoding="utf-8")

# --------------User data-------------------------------

users = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine",
    "admin": "4dm1N",  # admin
}

# ------------Basic Authentication setup

security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username = credentials.username
    password = credentials.password

    if username in users and users[username] == password:
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def is_admin(username: str = Depends(authenticate_user)) -> str:
    if username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return username


# ---------------Model----------------------
class Question(BaseModel):
    question: str
    subject: str
    use: str
    correct: str
    responseA: str
    responseB: str
    responseC: str
    responseD: Optional[str] = None
    remark: Optional[str] = None


class QuestionResponse(BaseModel):
    message: str
    question: Question


# --------------------------------No registration endpoints-------------------------
@app.get("/", name="No api")
def get_index():
    return {"message": "There is no application here!"}


@app.get("/verify", name="Api health check", tags=["Api health check"])
def verify():
    return {"message": "I'm ok! Welcome!"}


# ---------------------------------Admin only endpoints---------------------------------
@app.get(
    "/questions/",
    response_model=List[Question],
    name="Questions all",
    tags=["Admin Tasks"],
)
def get_questions(username: str = Depends(is_admin)):
    """Only for admin! All questions are here!"""

    if df.empty:
        raise HTTPException(status_code=404, detail="No questions found.")
    return df.fillna("").to_dict(orient="records")


@app.get(
    "/questions/subject/{subject}",
    response_model=List[Question],
    name="Subjects related to questions",
    tags=["Admin Tasks"],
)
def get_questions_by_subject(subject: str, username: str = Depends(is_admin)):
    """For test--- subject : BDD, Data Science."""

    filtered = df[df["subject"] == subject].fillna("").to_dict(orient="records")
    if not filtered:
        raise HTTPException(
            status_code=404, detail=f"No questions found for subject: {subject}"
        )
    return filtered


@app.post(
    "/questions/",
    response_model=QuestionResponse,
    name="Add question",
    tags=["Admin Tasks"],
)
def create_question(question: Question, username: str = Depends(is_admin)):
    """For test--- subject : BDD, Data Science.--- use: Test de positionnement, Total Bootcamp---"""

    new_question = question.model_dump()  # dict() is depricated, model_dump() insted
    global df
    df = pd.concat([df, pd.DataFrame([new_question])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    return ({"message": "Question added successfully!", "question": new_question},)


# ------------------------------ Users endpoint--------------------------------------------
@app.get(
    "/generate-mcq/",
    response_model=List[Question],
    name="Generate a new QUIZ",
    tags=["ALL users task"],
)
def generate_mcq(
    # subjects: List[str] = Query(...),
    # use: str = Query(...),
    # num_questions: int = Query(...),
    # username: str = Depends(authenticate_user),
    subjects: List[str] = Query(
        ..., title="Subjects", description="Enter the subjects"
    ),
    use: str = Query(..., title="Use Type", description="Enter the type of test(use)"),
    num_questions: int = Query(
        ..., title="Number of Questions", description="Enter the number of questions"
    ),
):
    """For test--- subject : BDD, Data Science.--- use: Test de positionnement, Total Bootcamp---questions. 5, 10, 20"""

    if num_questions not in [5, 10, 20]:
        raise HTTPException(
            status_code=400, detail="Number of questions must be 5, 10, or 20."
        )

    filtered = df[(df["use"] == use) & (df["subject"].isin(subjects))]
    if filtered.empty:
        raise HTTPException(status_code=404, detail="No questions found.")
    if len(filtered) < num_questions:
        raise HTTPException(status_code=400, detail="Not enough questions available.")
    #   filtered = df[df["subject"] == subjects].fillna("").to_dict(orient="records")

    sampled = filtered.sample(n=num_questions).fillna("").to_dict(orient="records")
    return sampled


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
# uvicorn main:app --reload
