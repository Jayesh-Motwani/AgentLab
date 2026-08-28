'''this is where we define our output schemas, state schemas for graph agents 
and typed schemas for various tasks'''

from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    subject: str
    contents: str
    invalid_request: bool | None = Field(default=False)
