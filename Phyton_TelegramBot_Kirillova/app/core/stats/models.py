from datetime import date as date_type

from sqlalchemy import BigInteger, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.postgres.base import Base


class BotStatistics(Base):
    __tablename__ = "bot_statistics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, unique=True, index=True)

    user_count: Mapped[int] = mapped_column(Integer, default=0)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    edited_events: Mapped[int] = mapped_column(Integer, default=0)
    cancelled_events: Mapped[int] = mapped_column(Integer, default=0)