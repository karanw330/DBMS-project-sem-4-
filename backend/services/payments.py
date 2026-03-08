from fastapi import APIRouter, HTTPException
from backend.models import PaymentCreate, PaymentOut
import backend.data as db
from datetime import datetime, timedelta
import qrcode
import base64
from io import BytesIO

router = APIRouter()

@router.post("/", response_model=PaymentOut)
def convert_payment(pay_in: PaymentCreate):
    # Find subscription
    sub = next((s for s in db.subscriptions if s["id"] == pay_in.subscription_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # 1. Create Payment
    new_payment = {
        "id": db.payment_id_counter,
        "subscription_id": pay_in.subscription_id,
        "amount": pay_in.amount,
        "status": "success" # IMMEDIATE SUCCESS
    }
    db.payment_id_counter += 1
    db.payments.append(new_payment)

    # 2. Activate Subscription
    # Get plan duration
    plan = next((p for p in db.plans if p["id"] == sub["plan_id"]), None)
    duration_days = plan["duration_days"] if plan else 30
    
    now = datetime.now()
    sub["status"] = "active"
    sub["start_date"] = now.isoformat()
    sub["renewal_date"] = (now + timedelta(days=duration_days)).isoformat()
    
    return new_payment

@router.get("/generate-qr")
def generate_qr(amount: float, order_id: int, user_id: int, base_url: str = None):
    print(f"--- QR GEN DEBUG ---")
    print(f"amount: {amount}, order_id: {order_id}, user_id: {user_id}, base_url: {base_url}")
    
    # data = "https://dbms-project-sem-4.vercel.app/"

    data = f"https://dbms-project-sem-4.vercel.app/payment/upi.html?sub_id={order_id}"
    
    # # If base_url is provided, create a link to index.html for checkout
    # if base_url:
    #     # baseUrl should be http://127.0.0.1:3000/frontend
    #     sep = "" if base_url.endswith("/") else "/"
    #     data_str = f"{base_url}{sep}index.html?sub_id={order_id}"
    # else:
    #     # Fallback to JSON data if no base_url provided
    #     data = {
    #         "amount": amount,
    #         "order_id": order_id,
    #         "user_id": user_id,
    #         "merchant": "Billing Sys"
    #     }
    #     import json
    #     data_str = json.dumps(data)
    #     print(f"Encoding JSON: {data_str}")
    
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {"qr_base64": qr_base64, "encoded_data": data}

from backend.models import UPIPaymentRequest

@router.post("/upi-payment")
def upi_payment(req: UPIPaymentRequest):
    # 1. Find user
    user = next((u for u in db.users if u["id"] == req.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Check role
    if user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Access denied: Only users can make UPI payments")
    
    # 3. Check PIN
    if user.get("upi") != req.pin:
        raise HTTPException(status_code=401, detail="Incorrect UPI PIN")
    
    # 4. Find subscription
    sub = next((s for s in db.subscriptions if s["id"] == req.subscription_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # 5. Activate Subscription
    plan = next((p for p in db.plans if p["id"] == sub["plan_id"]), None)
    duration_days = plan["duration_days"] if plan else 30
    
    now = datetime.now()
    sub["status"] = "active"
    sub["start_date"] = now.isoformat()
    sub["renewal_date"] = (now + timedelta(days=duration_days)).isoformat()
    
    # 6. Create Payment Record
    new_payment = {
        "id": db.payment_id_counter,
        "subscription_id": req.subscription_id,
        "amount": plan["price"] if plan else 0.0,
        "status": "success"
    }
    db.payment_id_counter += 1
    db.payments.append(new_payment)
    
    return {"status": "success", "message": "Payment successful and subscription activated"}
