import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, Tariff, User, Subscription


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None
) -> User:
    user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
    elif user.username != username:          # додано
        user.username = username             # додано
        await session.commit()               # додано
    return user


async def get_active_tariffs(session: AsyncSession) -> list[Tariff]:
    result = await session.scalars(
        select(Tariff).where(Tariff.is_active).order_by(Tariff.price)
    )
    return list(result)


async def get_tariff(session: AsyncSession, tariff_id: int) -> Tariff | None:
    return await session.get(Tariff, tariff_id)


async def create_order(session: AsyncSession, user: User, tariff: Tariff) -> Order:
    order = Order(
        order_uuid=uuid.uuid4().hex,
        user_id=user.id,
        tariff_id=tariff.id,
        amount=tariff.price,  # фіксуємо ціну на момент замовлення
    )
    session.add(order)
    await session.commit()
    return order


async def get_order_for_update(session: AsyncSession, order_uuid: str) -> Order | None:
    # with_for_update блокує рядок, поки не завершиться транзакція:
    # два одночасні callback не обробляться паралельно
    return await session.scalar(
        select(Order).where(Order.order_uuid == order_uuid).with_for_update()
    )


async def get_active_subscription(
    session: AsyncSession, user_id: int
) -> Subscription | None:
    return await session.scalar(
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.is_active)
        .order_by(Subscription.id.desc())
        .limit(1)
    )