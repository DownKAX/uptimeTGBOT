from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from datetime import datetime

Base = declarative_base()

class Users(Base):
  __tablename__ = 'users'
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
  username: Mapped[str] = mapped_column(unique=True, nullable=False)
  password: Mapped[str] = mapped_column(unique=False, nullable=False)
  email: Mapped[str] = mapped_column(unique=True, nullable=False)
  telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
  register_time: Mapped[datetime] = mapped_column(unique=False, nullable=False)

class Urls(Base):
  __tablename__ = 'urls'
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
  url: Mapped[str] = mapped_column(unique=True, nullable=False)
  time_added_seconds: Mapped[int] = mapped_column(unique=False, nullable=False)
  used_by_counter: Mapped[int] = mapped_column(unique=False, nullable=False)
  status: Mapped[str] = mapped_column(unique=False, nullable=False)

class UsersUrls(Base):
  __tablename__ = 'users_urls'
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=False)
  url_id: Mapped[str] = mapped_column(ForeignKey('urls.id', ondelete='CASCADE'), unique=False, nullable=False)

class Incidents(Base):
    __tablename__ = 'incidents'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    url_id: Mapped[int] = mapped_column(ForeignKey('urls.id', ondelete='CASCADE'), nullable=False, unique=True)
    started_at: Mapped[datetime] = mapped_column(unique=False, nullable=False)
    ended_at:  Mapped[datetime] = mapped_column(unique=False, nullable=True)
    duration: Mapped[int] = mapped_column(unique=False, nullable=True)

































































