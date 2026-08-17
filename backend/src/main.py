import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.db import init_db
from api.chat.router import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before the app startup
    init_db()
    yield
    # after app startup

app = FastAPI(lifespan=lifespan)
app.include_router(chat_router, prefix="/api/chat")

MY_PROJECT = os.environ.get("MY_PROJECT_NAME")
API_KEY = os.environ.get("API_KEY")


@app.get("/")
async def read_root():
    return {"Hello": "World AGAIN!", "project_name": MY_PROJECT}
