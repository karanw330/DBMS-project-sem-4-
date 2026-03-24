from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import PlanCreate, PlanOut
from backend.database import get_db_connection

router = APIRouter()

@router.post("/", response_model=PlanOut)
def create_plan(plan_in: PlanCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO plans (company_id, plan_name, description, price, duration_days, image_url) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (plan_in.company_id, plan_in.plan_name, plan_in.description, 
             plan_in.price, plan_in.duration_days, plan_in.image_url)
        )
        plan_id = cursor.lastrowid
        conn.commit()
        
        return {**plan_in.dict(), "id": plan_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.get("/", response_model=List[PlanOut])
def get_plans(company_id: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if company_id:
        cursor.execute("SELECT * FROM plans WHERE company_id = ?", (company_id,))
    else:
        cursor.execute("SELECT * FROM plans")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM plans WHERE id = ?", (plan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    
    raise HTTPException(status_code=404, detail="Plan not found")
