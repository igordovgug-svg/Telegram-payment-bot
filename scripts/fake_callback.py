import base64
import json
import random
import sys
import urllib.parse
import urllib.request

from app.services.liqpay import make_signature

order_uuid, amount = sys.argv[1], float(sys.argv[2])
payload = {
    "order_id": order_uuid,
    "status": "sandbox",
    "amount": amount,
    "currency": "UAH",
    "payment_id": random.randint(10**8, 10**9),
}
data = base64.b64encode(json.dumps(payload).encode()).decode()
body = urllib.parse.urlencode({"data": data, "signature": make_signature(data)}).encode()
print(urllib.request.urlopen("http://127.0.0.1:8000/liqpay/callback", data=body).read())