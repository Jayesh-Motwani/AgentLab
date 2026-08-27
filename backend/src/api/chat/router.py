from fastapi import APIRouter, Depends
from api.chat.models import ChatMessagePayload, ChatMessage
from sqlmodel import Session
from api.db import get_session

router = APIRouter()


@router.get("/")
def chat_health():
    return {"status": "ok"}


# HTTP POST -> payload = {"message": "Hello"} -> {"message": "Hello", "id": 1}
# curl -X POST -d '{"message": "Hello_World"}' http://localhost:8080/api/chats/
# response_model lets us serialize our payload
@router.post("/", response_model=ChatMessage)
def chat_create_message(
    payload: ChatMessagePayload,
    session: Session = Depends(get_session)
):

    data = payload.model_dump()  # Pydantic function that turns payload into dictionary
    # this validates payload has fields that are required by schema
    obj = ChatMessage.model_validate(data)

    # ready to store in the database
    session.add(obj)
    session.commit()  # obj won't be in the database until we commit
    session.refresh(obj)  # ensures primary key is added to payload instance

    return obj
