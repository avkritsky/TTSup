from pydantic import BaseModel


class NewUser(BaseModel):
    login: str
    password: str
    chat_id: str | None = None
    fullname: str | None = None


class NewUserResult(BaseModel):
    id: int
    login: str
    group: str


class ErrorNewUser(BaseModel):
    error: str
    login: str
