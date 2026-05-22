import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Category(str, enum.Enum):
    AUTO = "auto"
    REALESTATE = "realestate"
    PHONE = "phone"
    JOBS = "jobs"


CATEGORY_LABELS = {
    Category.AUTO: "🚗 Avto",
    Category.REALESTATE: "🏠 Uy-joy",
    Category.PHONE: "📱 Telefon",
    Category.JOBS: "💼 Bo'sh ish o'rinlari",
}


class AdStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Ad(TimestampMixin, Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category: Mapped[Category] = mapped_column(Enum(Category, name="category_enum"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(20))
    photo_file_ids: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    status: Mapped[AdStatus] = mapped_column(
        Enum(AdStatus, name="ad_status_enum"), default=AdStatus.DRAFT
    )
    admin_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    main_channel_message_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="ads")  # noqa: F821
