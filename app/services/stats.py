from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, Subscription, Tariff, User


async def get_stats(session: AsyncSession) -> dict:
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)

    paid_count, revenue = (
        await session.execute(
            select(func.count(Order.id), func.coalesce(func.sum(Order.amount), 0))
            .where(Order.status == "paid")
        )
    ).one()

    revenue_30 = await session.scalar(
        select(func.coalesce(func.sum(Order.amount), 0))
        .where(Order.status == "paid", Order.paid_at >= month_ago)
    )
    pending = await session.scalar(
        select(func.count(Order.id)).where(Order.status == "pending")
    )
    users = await session.scalar(select(func.count(User.id)))
    active_subs = await session.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active)
    )
    return {
        "users": users,
        "active_subs": active_subs,
        "paid_count": paid_count,
        "revenue": revenue,
        "revenue_30": revenue_30,
        "pending": pending,
    }


async def get_last_payments(session: AsyncSession, limit: int = 10):
    result = await session.execute(
        select(Order, User, Tariff)
        .join(User, User.id == Order.user_id)
        .join(Tariff, Tariff.id == Order.tariff_id)
        .where(Order.status == "paid")
        .order_by(Order.paid_at.desc())
        .limit(limit)
    )
    return result.all()


async def get_active_subscribers(session: AsyncSession, limit: int = 20):
    result = await session.execute(
        select(Subscription, User)
        .join(User, User.id == Subscription.user_id)
        .where(Subscription.is_active)
        .order_by(Subscription.expires_at.asc().nulls_last())
        .limit(limit)
    )
    return result.all()