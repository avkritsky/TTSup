from pydantic import BaseModel, ConfigDict


class NewTicketRequest(BaseModel):
    text: str


class NewTicketResponse(BaseModel):
    id: int
    author_login: str
