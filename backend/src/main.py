import os
from fastapi import FastAPI

app = FastAPI()

MY_PROJECT = os.environ.get("MY_PROJECT_NAME")
API_KEY = os.environ.get("API_KEY")


@app.get("/")
async def read_root():
    return {"Hello": "World AGAIN!", "project_name": MY_PROJECT}
