from sqlmodel import SQLModel, Field, DateTime
from datetime import datetime, timezone


def get_utc_now():
    return datetime.now().replace(tzinfo=timezone.utc)  # gets time in utc timezone


class ChatMessagePayload(SQLModel):
    # Pydantic style payload validation class
    message: str


class ChatMessage(SQLModel, table=True):
    # This is database table
    id: int | None = Field(default=None, primary_key=True)
    message: str  # If we don't allow a None value using | the fields are required fields by default
    created_at: datetime = Field(
        # calls get_utc_now function when we create a new chatmessage and sets data
        default_factory=get_utc_now,
        sa_type=DateTime(timezone=True),  # Timezone aware time added to the db
        # we can use timestamp as primary key if we use a timescaledb for time series data
        primary_key=False,
        nullable=False,
    )


class ChatMessageResponseList(SQLModel):
    message: str
    created_at: datetime = Field(default=None)
