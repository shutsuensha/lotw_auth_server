from pydantic import BaseModel


class SessionToken(BaseModel):
    session_id: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class UserPayloadJWT(BaseModel):
    user_id: int
    possible_username: str | None = None
    possible_avatar: str | None = None
