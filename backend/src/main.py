import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db import init_db
from api.chat.router import router as chat_router


CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://frontend,http://localhost"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan, title="Docker Learn API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router, prefix="/api/chat")

MY_PROJECT = os.environ.get("MY_PROJECT_NAME", "Docker Learn")
API_KEY = os.environ.get("API_KEY")


@app.get("/")
async def read_root():
    return {"message": "Docker Learn API is running", "project_name": MY_PROJECT}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
