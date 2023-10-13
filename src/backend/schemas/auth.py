from pydantic import BaseModel


class NewUser(BaseModel):
    login: str
    password: str
    chat_id: str
    fullname: str | None = None
