from pydantic import BaseModel, Field


class VkUserOut(BaseModel):
    id: int
    vk_id: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True


class VkUserIn(BaseModel):
    vk_id: str = Field(alias="user_id")
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar: str | None = None
    email: str | None = None

    class Config:
        extra = "ignore"
