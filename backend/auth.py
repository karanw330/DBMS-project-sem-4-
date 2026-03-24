from fastapi import APIRouter, HTTPException
from backend.models import UserLogin, UserRegister, UserOut
from backend.data import users, user_id_counter

router = APIRouter()

@router.post("/login", response_model=UserOut)
def login(user_in: UserLogin):
    for u in users:
        if u["email"] == user_in.email and u["password"] == user_in.password:
            return u
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register", response_model=UserOut)
def register(user_in: UserRegister):
    # Check if email exists
    for u in users:
        if u["email"] == user_in.email:
             raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate UPI PIN for users
    if user_in.role == "user":
        if user_in.upi_pin is None:
            raise HTTPException(status_code=400, detail="UPI PIN is required for user accounts")
        if not (0 <= user_in.upi_pin <= 9999):
            raise HTTPException(status_code=400, detail="UPI PIN must be a 4-digit number (0000-9999)")
    
    import backend.data as db
    
    new_user = {
        "id": db.user_id_counter,
        "name": user_in.name,
        "email": user_in.email,
        "password": user_in.password,
        "role": user_in.role
    }
    
    # Store UPI PIN only for user accounts
    if user_in.role == "user":
        new_user["upi"] = user_in.upi_pin
    
    db.users.append(new_user)
    db.user_id_counter += 1
    
    return new_user
