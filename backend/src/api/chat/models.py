from sqlmodel import SQLModel, Field


class ChatMessagePayload(SQLModel):
    # Pydantic style payload validation class
    message: str


class ChatMessage(SQLModel, table=True):
    # This is database table
    id: int | None = Field(default=None, primary_key=True)
    message: str  # If we don't allow a None value using | the fields are required fields by default
