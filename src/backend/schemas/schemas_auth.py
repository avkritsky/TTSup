from pydantic import BaseModel, ConfigDict


class NewUserRequest(BaseModel):
    login: str
    password: str
    chat_id: str | None = None
    fullname: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    group: str
    access_token: str
    refresh_token: str


class NewUserError(BaseModel):
    error: str
    login: str
