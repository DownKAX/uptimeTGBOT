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

class users_urls(Urls):
  __tablename__ = 'users_urls'
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=False)
  url: Mapped[str] = mapped_column(ForeignKey('urls.id', ondelete='CASCADE'), unique=False, nullable=False)
