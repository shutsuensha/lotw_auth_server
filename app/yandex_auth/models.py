from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class YandexUser(Base):
    __tablename__ = "yandex_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    yandex_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    login: Mapped[str | None] = mapped_column(String, nullable=True)
    client_id: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    real_name: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    sex: Mapped[str | None] = mapped_column(String, nullable=True)
    default_email: Mapped[str | None] = mapped_column(String, nullable=True)
    emails: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    birthday: Mapped[str | None] = mapped_column(String, nullable=True)
    default_avatar_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_avatar_empty: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    default_phone: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    psuid: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
