from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import SubscriptionCreate, SubscriptionOut
import backend.data as db

router = APIRouter()

@router.post("/", response_model=SubscriptionOut)
def create_subscription(sub_in: SubscriptionCreate):
    # Basic check if user and plan exist
    user_exists = any(u["id"] == sub_in.user_id for u in db.users)
    plan_exists = any(p["id"] == sub_in.plan_id for p in db.plans)
    
    if not user_exists or not plan_exists:
        raise HTTPException(status_code=404, detail="User or Plan not found")

    new_sub = {
        "id": db.sub_id_counter,
        "user_id": sub_in.user_id,
        "plan_id": sub_in.plan_id,
        "status": "pending", # Initial status before payment
        "start_date": None,
        "renewal_date": None
    }
    db.sub_id_counter += 1
    db.subscriptions.append(new_sub)
    return new_sub

@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(user_id: int = None, plan_id: int = None):
    results = db.subscriptions
    if user_id:
        results = [s for s in results if s["user_id"] == user_id]
    if plan_id:
        results = [s for s in results if s["plan_id"] == plan_id]
    return results
