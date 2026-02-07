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
    
    global user_id_counter
    # Need to access the global counter from data.py, but it's an integer so we can't modify it directly via import easily unless we mutated a mutable object or used a class. 
    # For simplicity in this script-like setup, we'll re-implement the counter increment or just import the module differently.
    # Actually, importing 'backend.data' gives us the module.
    import backend.data as db
    
    new_user = {
        "id": db.user_id_counter,
        "name": user_in.name,
        "email": user_in.email,
        "password": user_in.password,
        "role": user_in.role
    }
    db.users.append(new_user)
    db.user_id_counter += 1
    
    return new_user
