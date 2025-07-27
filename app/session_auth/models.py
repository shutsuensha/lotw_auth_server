from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SessionUser(Base):
    __tablename__ = "sessions_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    vk_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("vk_users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    yandex_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("yandex_users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
