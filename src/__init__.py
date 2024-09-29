from typing import Any, TypedDict


from pymongo import MongoClient
from pymongo.database import Database
from requests import request
from requests.exceptions import Timeout


LEETCODE_API_URL = "http://localhost:3000"
DB_URL = "mongodb://localhost:27017"
DB_CLIENT = MongoClient(DB_URL)


class TestCase(TypedDict):
    input: Any
    output: Any


class Question:

    def __init__(self, title: str) -> None:
        self.title = title
        question = request(
            "GET", f"{LEETCODE_API_URL}/select?titleSlug={self.title}"
        ).json()

        self.id: int = int(question["id"])
        self.description: str = question["question"]
        self.tags: list[str] = [x["slug"] for x in question["topicTags"]]

        test_cases: list[str] = question["exampleTestcases"].splitlines()
        self.test_cases: list[TestCase] = [
            TestCase(input=x, output=y)
            for x, y in zip(test_cases[::2], test_cases[1::2])
        ]


if "questions" not in DB_CLIENT.list_database_names():
    print("Questions database not found, creating one")

    try:
        request("GET", LEETCODE_API_URL, timeout=5)
    except Timeout:
        print(
            "Server not running, start a local instance as described in https://github.com/alfaarghya/alfa-leetcode-api/blob/main/CONTRIBUTING.md"
        )
        exit(1)

    num_qns = request("GET", f"{LEETCODE_API_URL}/problems?limit=1").json()[
        "totalQuestions"
    ]

    print(f"Downloading {num_qns} questions")
    _questions = request("GET", f"{LEETCODE_API_URL}/problems?limit={num_qns}").json()
    questions: list[Question] = [Question(qn["titleSlug"]) for qn in _questions]

    with DB_CLIENT.start_session() as session:
        print("Writing to database")
        db: Database = DB_CLIENT.questions
        db.create_collection(
            "questions",
            validator={
                "title": {"$type": "string"},
                "id": {"$type": "int"},
                "description": {"$type": "string"},
                "tags": {"$type": "array"},
                "test_cases": {"$type": "array"},
            },
        )
        db.questions.insert_many([qn.__dict__ for qn in questions])
