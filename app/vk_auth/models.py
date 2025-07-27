from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class VkUser(Base):
    __tablename__ = "vk_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vk_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
