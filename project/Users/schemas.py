from pydantic import BaseModel


class UsersAdd(BaseModel):
    username: str
    password: str


class UsersGet(BaseModel):
    id: int
    username: str
