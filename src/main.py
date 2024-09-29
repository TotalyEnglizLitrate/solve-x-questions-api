from typing import Literal

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from src import DB_URL

DB_CLIENT = AsyncMongoClient(DB_URL)
QUESTION_COLLECTION = DB_CLIENT.questions.get_collection("questions")

app = FastAPI()


@app.get("/")
async def list_endpoints():
    return {}


@app.get("/question")
async def get_question(get_by: Literal["id", "title"], value: int | str):
    if get_by not in {"id", "title"}:
        return {"error": "Invalid get_by parameter"}, 201

    if get_by == "id" and not isinstance(value, int):
        return {"error": "Invalid value for id"}, 201
    if get_by == "title" and not isinstance(value, str):
        return {"error": "Invalid value for title"}, 201

    return await QUESTION_COLLECTION.find_one({get_by: value})
