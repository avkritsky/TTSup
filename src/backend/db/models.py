from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    CheckConstraint,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from src.backend.core import config


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user' if config.IS_PROD else 'user_test'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    fullname: Mapped[str] = mapped_column(String(100))
    group: Mapped[list[str]] = mapped_column(
        String(10),
        CheckConstraint('"group" in ' + "('admin', 'user', 'support')"),
        nullable=False,
    )
    # for telegram chat ID (send answer for user in telegram)
    chat_id: Mapped[str] = mapped_column(
        String(30),
        default=None,
        nullable=True,
    )

    @property
    def jwt_model(self) -> dict:
        res = {
            'id': self.id,
            'login': self.login,
            'group': self.group,
        }
        return res


class Ticket(Base):
    __tablename__ = 'ticket' if config.IS_PROD else 'ticket_test'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # who create ticket
    author_login: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )
    # where create ticket
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )
    # where was last update
    last_update: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )
    # is ticket closed?
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    # ticket states
    state: Mapped[str] = mapped_column(
        String(13),
        CheckConstraint(
            '"state" in ' + "('new', 'await user', 'await support', 'closed')"
        ),
        nullable=False,
        default='new',
    )

    text: Mapped[str] = mapped_column(String(255), nullable=False)

    dialogs: Mapped[list["TicketDialog"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    @property
    def created_json(self) -> dict:
        res = {
            'id': self.id,
            'author_login': self.author_login,
        }
        return res

    @property
    def ticket_json(self) -> dict:
        res = {
            'id': self.id,
            'author_login': self.author_login,
            'text': self.text,
            'state': self.state,
            'create_time': self.create_time.isoformat(sep=' '),
            'last_update': self.last_update.isoformat(sep=' '),
        }
        return res

    def close(self):
        self.is_closed = True
        self.state = 'closed'
        self._update_time()

    def _update_time(self):
        self.last_update = datetime.now()


class TicketDialog(Base):
    __tablename__ = 'ticket_dialog' if config.IS_PROD else 'ticket_dialog_test'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey(f"{Ticket.__tablename__}.id")
    )

    text: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(30), nullable=False)
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )

    ticket: Mapped[Ticket] = relationship(back_populates="dialogs")
