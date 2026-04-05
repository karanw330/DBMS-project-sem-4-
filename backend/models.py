from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserLogin(UserBase):
    password: str

class UserRegister(UserBase):
    name: str
    password: str
    role: Literal["user", "company"]
    phone_number: str
    upi_pin: Optional[int] = None  # Required for role='user'

class UserOut(UserBase):
    id: int
    name: str
    role: str
    phone_number: str

class PlanCreate(BaseModel):
    company_id: int
    plan_name: str
    description: str
    price: float
    duration_days: int
    image_url: Optional[str] = None

class PlanOut(PlanCreate):
    id: int

class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int

class SubscriptionOut(BaseModel):
    name: Optional[str] = None
    id: int
    user_id: int
    plan_id: int
    plan_name: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None
    status: str
    start_date: Optional[str]
    end_date: Optional[str]

class PaymentCreate(BaseModel):
    subscription_id: int
    amount: float

class PaymentOut(PaymentCreate):
    id: int
    status: str
    payment_date: Optional[str] = None
    payment_method: Optional[str] = None

class UPIPaymentRequest(BaseModel):
    user_id: int
    subscription_id: int
    pin: int
