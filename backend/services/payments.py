from fastapi import APIRouter, HTTPException
from backend.models import PaymentCreate, PaymentOut, UPIPaymentRequest
from backend.database import get_db_connection
from datetime import datetime, timedelta
import qrcode
import base64
from io import BytesIO

router = APIRouter()

@router.post("/", response_model=PaymentOut)
def convert_payment(pay_in: PaymentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.*, p.duration_days 
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.id
            WHERE s.id = ?
        """, (pay_in.subscription_id,))
        sub = cursor.fetchone()
        
        if not sub:
            conn.close()
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        now = datetime.now()
        start_date = now.isoformat()
        end_date = (now + timedelta(days=sub["duration_days"])).isoformat()
        payment_date = now.isoformat()

        cursor.execute(
            """INSERT INTO payments (subscription_id, amount, status, payment_date, payment_method) 
               VALUES (?, ?, 'success', ?, 'Standard')""",
            (pay_in.subscription_id, pay_in.amount, payment_date)
        )
        payment_id = cursor.lastrowid

        cursor.execute(
            "UPDATE subscriptions SET status = 'active', start_date = ?, end_date = ? WHERE id = ?",
            (start_date, end_date, pay_in.subscription_id)
        )

        conn.commit()
        
        return {
            "id": payment_id,
            "subscription_id": pay_in.subscription_id,
            "amount": pay_in.amount,
            "status": "success",
            "payment_date": payment_date,
            "payment_method": "Standard"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.get("/generate-qr")
def generate_qr(amount: float, order_id: int, user_id: int):
    data = f"https://dbms-project-sem-4.vercel.app/payment/upi.html?sub_id={order_id}&user_id={user_id}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO qr_codes (qr_data, generated_at) VALUES (?, ?)",
            (data, datetime.now().isoformat())
        )
        conn.commit()
    except:
        pass 
    finally:
        conn.close()

    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {"qr_base64": qr_base64, "encoded_data": data}

@router.post("/upi-payment")
def upi_payment(req: UPIPaymentRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT role, upi_pin FROM users WHERE id = ?", (req.user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        if user["role"] != "user":
            conn.close()
            raise HTTPException(status_code=403, detail="Access denied: Only users can make UPI payments")
        
        if user["upi_pin"] != req.pin:
            conn.close()
            raise HTTPException(status_code=401, detail="Incorrect UPI PIN")
        
        cursor.execute("""
            SELECT s.*, p.price, p.duration_days 
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.id
            WHERE s.id = ?
        """, (req.subscription_id,))
        sub = cursor.fetchone()
        
        if not sub:
            conn.close()
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        now = datetime.now()
        start_date = now.isoformat()
        end_date = (now + timedelta(days=sub["duration_days"])).isoformat()
        payment_date = now.isoformat()

        cursor.execute(
            """INSERT INTO payments (subscription_id, amount, status, payment_date, payment_method) 
               VALUES (?, ?, 'success', ?, 'UPI')""",
            (req.subscription_id, sub["price"], payment_date)
        )
        
        cursor.execute(
            "UPDATE subscriptions SET status = 'active', start_date = ?, end_date = ? WHERE id = ?",
            (start_date, end_date, req.subscription_id)
        )

        conn.commit()
        return {"status": "success", "message": "Payment successful and subscription activated"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()
