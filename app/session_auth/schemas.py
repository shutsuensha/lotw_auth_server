from pydantic import BaseModel


class SessionToken(BaseModel):
    session_id: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class UserPayloadJWT(BaseModel):
    vk_id: str | None = None
    yandex_id: str | None = None
    possible_username: str | None = None
    possible_avatar: str | None = None
