from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    full_name: Mapped[str] = mapped_column(String(255))

    ads: Mapped[list["Ad"]] = relationship(back_populates="user")  # noqa: F821
