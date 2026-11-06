from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, Subscription, Tariff


async def activate_subscription(
    session: AsyncSession, order: Order, tariff: Tariff
) -> Subscription:
    now = datetime.now(timezone.utc)
    current = await session.scalar(
        select(Subscription)
        .where(Subscription.user_id == order.user_id, Subscription.is_active)
        .order_by(Subscription.id.desc())
        .limit(1)
    )

    if current is None:
        expires = (
            None if tariff.duration_days is None
            else now + timedelta(days=tariff.duration_days)
        )
        sub = Subscription(
            user_id=order.user_id,
            order_id=order.id,
            starts_at=now,
            expires_at=expires,
        )
        session.add(sub)
        return sub

    # Продовження: подовжуємо наявну підписку, а не створюємо другу
    if current.expires_at is None:        # вже «назавжди»
        return current
    if tariff.duration_days is None:      # купив «назавжди»
        current.expires_at = None
    else:
        base = max(now, current.expires_at)
        current.expires_at = base + timedelta(days=tariff.duration_days)
    current.order_id = order.id
    current.reminder_sent = False
    return current