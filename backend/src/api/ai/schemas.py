'''this is where we define our output schemas, state schemas for graph agents 
and typed schemas for various tasks'''

from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    subject: str
    contents: str
    invalid_request: bool | None = Field(default=False)


class SearchQueries(BaseModel):
    queries: list[str]


class Source(BaseModel):
    title: str
    url: str
    publisher: str
    excerpt: str


class ResearchResult(BaseModel):
    answer: str
    sources: list[Source]
    confidence: str


class ReportFile(BaseModel):
    file_path: str


class SupervisorMessageSchema(BaseModel):
    content: str
