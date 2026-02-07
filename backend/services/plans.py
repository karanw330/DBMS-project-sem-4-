from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import PlanCreate, PlanOut
import backend.data as db

router = APIRouter()

@router.post("/", response_model=PlanOut)
def create_plan(plan_in: PlanCreate):
    new_plan = plan_in.dict()
    new_plan["id"] = db.plan_id_counter
    db.plan_id_counter += 1
    db.plans.append(new_plan)
    return new_plan

@router.get("/", response_model=List[PlanOut])
def get_plans(company_id: int = None):
    if company_id:
        return [p for p in db.plans if p["company_id"] == company_id]
    return db.plans

@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(plan_id: int):
    for p in db.plans:
        if p["id"] == plan_id:
            return p
    raise HTTPException(status_code=404, detail="Plan not found")
