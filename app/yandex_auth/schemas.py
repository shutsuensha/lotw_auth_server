from pydantic import BaseModel, Field


class PhoneData(BaseModel):
    id: int
    number: str


class YandexUserIn(BaseModel):
    yandex_id: str = Field(alias="id")
    login: str | None = None
    client_id: str | None = None
    display_name: str | None = None
    real_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    sex: str | None = None
    default_email: str | None = None
    emails: list[str] | None = None
    birthday: str | None = None
    default_avatar_id: str | None = None
    is_avatar_empty: bool | None = None
    default_phone: PhoneData | None = None
    psuid: str | None = None

    class Config:
        extra = "ignore"


class YandexUserOut(BaseModel):
    id: int
    yandex_id: str
    login: str | None = None
    client_id: str | None = None
    display_name: str | None = None
    real_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    sex: str | None = None
    default_email: str | None = None
    emails: list[str] | None = None
    birthday: str | None = None
    default_avatar_id: str | None = None
    is_avatar_empty: bool | None = None
    default_phone: PhoneData | None = None
    psuid: str | None = None
    user_id: int

    class Config:
        from_attributes = True
