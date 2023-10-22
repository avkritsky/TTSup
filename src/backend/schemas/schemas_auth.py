from pydantic import BaseModel


class NewUser(BaseModel):
    login: str
    password: str
    chat_id: str | None = None
    fullname: str | None = None


class UserAuthData(BaseModel):
    id: int
    login: str
    group: str
    access_token: str
    refresh_token: str


class ErrorNewUser(BaseModel):
    error: str
    login: str
