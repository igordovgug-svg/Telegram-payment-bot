from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {datetime: DateTime(timezone=True)}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    duration_days: Mapped[int | None]  # None = назавжди
    is_active: Mapped[bool] = mapped_column(default=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_uuid: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(default="pending")  # pending/paid/failed
    liqpay_payment_id: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    paid_at: Mapped[datetime | None]


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    starts_at: Mapped[datetime]
    expires_at: Mapped[datetime | None]  # None = назавжди
    is_active: Mapped[bool] = mapped_column(default=True)
    reminder_sent: Mapped[bool] = mapped_column(default=False)