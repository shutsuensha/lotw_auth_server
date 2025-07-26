from datetime import datetime

from pydantic import BaseModel


class ServerIn(BaseModel):
    url: str
    name: str
    locale: str
    max_players: int
    status: str


class ServerOut(BaseModel):
    id: int
    url: str
    name: str
    locale: str
    max_players: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ServerOptionalIn(BaseModel):
    url: str | None = None
    name: str | None = None
    locale: str | None = None
    max_players: int | None = None
    status: str | None = None
