import logging
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.db.models import User, Tariff
from app.db.repositories import get_order_for_update
from app.services.access import create_invite_link    
from app.services.liqpay import decode_data, verify_signature
from app.services.subscriptions import activate_subscription 


router = APIRouter()
log = logging.getLogger(__name__)

PAID_STATUSES = {"success", "sandbox"} 
FAILED_STATUSES = {"failure", "error"}


@router.post("/liqpay/callback")
async def liqpay_callback(
    request: Request,
    data: str = Form(),
    signature: str = Form(),
    session: AsyncSession = Depends(get_session),
):
    if not verify_signature(data, signature):
        raise HTTPException(status_code=403, detail="bad signature")

    payload = decode_data(data)
    order = await get_order_for_update(session, payload.get("order_id", ""))
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")

    if order.status == "paid":
        return {"ok": True}

    status = payload.get("status")

    if status in PAID_STATUSES:
        if (
            Decimal(str(payload.get("amount"))) != order.amount
            or payload.get("currency") != "UAH"
        ):
            log.error("Amount mismatch for order %s: %s", order.order_uuid, payload)
            raise HTTPException(status_code=400, detail="amount mismatch")

        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        order.liqpay_payment_id = str(payload.get("payment_id"))

        tariff = await session.get(Tariff, order.tariff_id)           
        await activate_subscription(session, order, tariff)           
        await session.commit()  

        user = await session.get(User, order.user_id)
        bot = request.app.state.bot                                  

        try:
            await bot.send_message(
                user.telegram_id, f"Оплату за замовлення #{order.id} отримано ✅"
            )
        except Exception:
            log.exception("Не вдалося надіслати підтвердження")

        try:                                                         
            link = await create_invite_link(bot)
            await bot.send_message(
                user.telegram_id,
                f"Ваше посилання в канал (одноразове, діє 24 год):\n{link}",
            )
        except Exception:
            log.exception("Не вдалося видати доступ користувачу")

    elif status in FAILED_STATUSES:
        order.status = "failed"
        await session.commit()

    return {"ok": True}