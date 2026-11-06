import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.models import Tariff
from app.db.session import async_session

TARIFFS = [
    ("1 місяць", Decimal("199.00"), 30),
    ("3 місяці", Decimal("499.00"), 90),
    ("Назавжди", Decimal("1299.00"), None),
]


async def main() -> None:
    async with async_session() as session:
        exists = await session.scalar(select(Tariff.id).limit(1))
        if exists:
            print("Тарифи вже є, пропускаю")
            return
        session.add_all(
            Tariff(title=t, price=p, duration_days=d) for t, p, d in TARIFFS
        )
        await session.commit()
        print("Тарифи додано")


if __name__ == "__main__":
    asyncio.run(main())