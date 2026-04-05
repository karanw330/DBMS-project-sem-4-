from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import SubscriptionCreate, SubscriptionOut
from backend.database import get_db_connection

router = APIRouter()

@router.post("/", response_model=SubscriptionOut)
def create_subscription(sub_in: SubscriptionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM users WHERE id = ?", (sub_in.user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    cursor.execute("SELECT plan_name, price, image_url FROM plans WHERE id = ?", (sub_in.plan_id,))
    plan = cursor.fetchone()
    if not plan:
        conn.close()
        raise HTTPException(status_code=404, detail="Plan not found")

    try:
        cursor.execute(
            """INSERT INTO subscriptions (user_id, plan_id, status) 
               VALUES (?, ?, 'pending')""",
            (sub_in.user_id, sub_in.plan_id)
        )
        sub_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": sub_id,
            "user_id": sub_in.user_id,
            "plan_id": sub_in.plan_id,
            "plan_name": plan["plan_name"],
            "price": plan["price"],
            "image_url": plan["image_url"],
            "status": "pending",
            "start_date": None,
            "end_date": None
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(user_id: int = None, plan_id: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT u.name, s.*, p.plan_name, p.price, p.image_url 
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        JOIN users u ON s.user_id = u.id
        WHERE 1=1
    """
    params = []
    if user_id:
        query += " AND s.user_id = ?"
        params.append(user_id)
    if plan_id:
        query += " AND s.plan_id = ?"
        params.append(plan_id)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    print("rows:")
    print(rows)

    return [dict(row) for row in rows]

@router.get("/{sub_id}", response_model=SubscriptionOut)
def get_subscription(sub_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT u.name, s.*, p.plan_name, p.price, p.image_url 
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        JOIN users u ON s.user_id = u.id
        WHERE s.id = ? 
    """, (sub_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
        
    raise HTTPException(status_code=404, detail="Subscription not found")
