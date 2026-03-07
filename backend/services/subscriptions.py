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

    # Get plan info
    plan = next((p for p in db.plans if p["id"] == sub_in.plan_id), None)
    plan_name = plan["plan_name"] if plan else "Unknown Plan"
    image_url = plan["image_url"] if plan else None

    new_sub = {
        "id": db.sub_id_counter,
        "user_id": sub_in.user_id,
        "plan_id": sub_in.plan_id,
        "plan_name": plan_name,
        "image_url": image_url,
        "status": "pending", # Initial status before payment
        "start_date": None,
        "renewal_date": None
    }
    db.sub_id_counter += 1
    db.subscriptions.append(new_sub)
    print("subs-created:",db.subscriptions)
    return new_sub

@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(user_id: int = None, plan_id: int = None):
    results = db.subscriptions
    if user_id:
        results = [s for s in results if s["user_id"] == user_id]
    if plan_id:
        results = [s for s in results if s["plan_id"] == plan_id]
    
    # Enrich with plan details (name, image)
    enriched_results = []
    print("enriched_results:",enriched_results)
    for s in results:
        sub_copy = s.copy()
        plan = next((p for p in db.plans if p["id"] == s["plan_id"]), None)
        
        if "plan_name" not in sub_copy or not sub_copy["plan_name"]:
            sub_copy["plan_name"] = plan["plan_name"] if plan else "Unknown Plan"
        
        if "image_url" not in sub_copy or not sub_copy["image_url"]:
            sub_copy["image_url"] = plan["image_url"] if plan else None
            
        enriched_results.append(sub_copy)
        
    return enriched_results
