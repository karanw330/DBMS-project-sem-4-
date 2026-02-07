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
def generate_qr():
    data = "https://cryp-sim.vercel.app/"
    print("reached")
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {"qr_base64": qr_base64}
