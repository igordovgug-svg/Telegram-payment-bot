import base64
import hashlib
import hmac
import json
from urllib.parse import urlencode

from app.config import settings
from app.db.models import Order

CHECKOUT_URL = "https://www.liqpay.ua/api/3/checkout"


def make_signature(data: str) -> str:
    raw = settings.liqpay_private_key + data + settings.liqpay_private_key
    return base64.b64encode(hashlib.sha1(raw.encode()).digest()).decode()


def verify_signature(data: str, signature: str) -> bool:
    return hmac.compare_digest(make_signature(data), signature)


def build_checkout_url(order: Order, description: str) -> str:
    payload = {
        "version": 3,
        "public_key": settings.liqpay_public_key,
        "action": "pay",
        "amount": str(order.amount),
        "currency": "UAH",
        "description": description,
        "order_id": order.order_uuid,
        "server_url": f"{settings.public_url}/liqpay/callback",
        "sandbox": 1,
    }
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"{CHECKOUT_URL}?{urlencode({'data': data, 'signature': make_signature(data)})}"


def decode_data(data: str) -> dict:
    return json.loads(base64.b64decode(data))