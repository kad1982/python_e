from datetime import date as date_type, time as time_type

from sqlalchemy import BigInteger, Date, ForeignKey, String, Text, Time, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.postgres.base import Base


class Calendar(Base):
    __tablename__ = "calendar"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    date: Mapped[date_type] = mapped_column(Date)
    time: Mapped[time_type] = mapped_column(Time)
    details: Mapped[str] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)