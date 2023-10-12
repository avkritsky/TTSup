from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    fullname: Mapped[str] = mapped_column(String(100))
    group: Mapped[list[str]] = mapped_column(
        String(10),
        CheckConstraint("group in ('admin', 'user', 'support')"),
        nullable=False,
    )
    # for telegram chat ID (send answer for user in telegram)
    chat_id: Mapped[str] = mapped_column(String(30), default=None)
