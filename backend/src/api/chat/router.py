from typing import List
from fastapi import APIRouter, Depends, HTTPException
from api.chat.models import ChatMessagePayload, ChatMessage, ChatMessageResponseList
from sqlmodel import Session, select
from api.db import get_session
from api.ai.agents import get_supervisor

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


@router.post("/")
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

    supe = get_supervisor()
    msg_data = {
        "messages": [
            {"role": "user",
              "content": f"{payload.message}"},
        ]
    }

    try:
        response = supe.invoke(msg_data)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The AI service is currently rate-limited or unavailable. Please try again in a few minutes."
        ) from exc

    if not response:
        raise HTTPException(status_code=400, detail="Error with supervisor")
    messages = response.get("messages")
    if not messages:
        raise HTTPException(status_code=400, detail="Error with supervisor")
    last_message = messages[-1]
    content = getattr(last_message, "content", None)
    if content is None and isinstance(last_message, dict):
        content = last_message.get("content")
    if content is None:
        raise HTTPException(status_code=500, detail="No content returned from supervisor")

    if isinstance(content, list):
        content = "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )

    return {"content": str(content)}
