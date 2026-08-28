from typing import List
from fastapi import APIRouter, Depends
from api.chat.models import ChatMessagePayload, ChatMessage, ChatMessageResponseList
from sqlmodel import Session, select
from api.db import get_session
from api.ai.schemas import EmailMessage
from api.ai.services import generate_email_message

router = APIRouter()


@router.get("/")
def chat_health():
    return {"status": "ok"}

# /api/chat/recent/
# curl http://localhost:8080/api/chat/recent/ # Only this as it is a get method


@router.get("/recent/", response_model=List[ChatMessageResponseList])
def chat_list_messages(session: Session = Depends(get_session)):
    query = select(ChatMessage)  # sql -> query in python
    results = session.exec(query).fetchall()[:10]
    return results


# HTTP POST -> payload = {"message": "Hello"} -> {"message": "Hello", "id": 1}
# response_model lets us serialize our payload
'''
To test with our new response api in powershell
curl.exe - - % -X POST - H "Content-Type: application/json" - d "{\"message\":\"Set up an important meeting with Mr. Motwani\"}" http: // localhost: 8080/api/chat/
'''


@router.post("/", response_model=EmailMessage)
def chat_create_message(
    payload: ChatMessagePayload,
    session: Session = Depends(get_session)
):
    '''
    The chat message payload is what our api post method will post, it has  a message field which is
    where we will take user's query as input in main.py and that will be saved to db as well as be used
    to invoke the agent using generate_email_message(query) function
    '''

    data = payload.model_dump()  # Pydantic function that turns payload into dictionary
    # this validates payload has fields that are required by schema
    obj = ChatMessage.model_validate(data)

    # ready to store in the database
    session.add(obj)
    session.commit()  # obj won't be in the database until we commit
    # session.refresh(obj)  # ensures primary key is added to payload instance

    # The query here now is gonna be payload message
    response = generate_email_message(payload.message)
    return response
