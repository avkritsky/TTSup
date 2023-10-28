from pydantic import BaseModel, ConfigDict


class NewTicketRequest(BaseModel):
    text: str


class NewTicketResponse(BaseModel):
    id: int
    author_login: str


class OneTicket(BaseModel):
    id: int
    author_login: str
    text: str
    state: str
    create_time: str
    last_update: str


class GetTicketsResponse(BaseModel):
    items: list[OneTicket]
