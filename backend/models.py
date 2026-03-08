from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

# Users
class UserBase(BaseModel):
    email: str

class UserLogin(UserBase):
    password: str

class UserRegister(UserBase):
    name: str
    password: str
    role: Literal["user", "company"]

class UserOut(UserBase):
    id: int
    name: str
    role: str

# Plans
class PlanCreate(BaseModel):
    company_id: int
    plan_name: str
    price: float
    duration_days: int
    image_url: Optional[str] = None

class PlanOut(PlanCreate):
    id: int

# Subscriptions
class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int

class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    plan_name: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None
    status: str
    start_date: Optional[str]
    renewal_date: Optional[str]

# Payments
class PaymentCreate(BaseModel):
    subscription_id: int
    amount: float

class PaymentOut(PaymentCreate):
    id: int
    status: str

class UPIPaymentRequest(BaseModel):
    user_id: int
    subscription_id: int
    pin: str
