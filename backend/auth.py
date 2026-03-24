from fastapi import APIRouter, HTTPException
from backend.models import UserLogin, UserRegister, UserOut
from backend.database import get_db_connection, hash_password

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "pong"}

@router.post("/login", response_model=UserOut)
def login(user_in: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_pwd = hash_password(user_in.password)
    
    cursor.execute(
        "SELECT id, name, email, role, phone FROM users WHERE email = ? AND password = ?",
        (user_in.email, hashed_pwd)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
            "phone_number": row["phone"]
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register", response_model=UserOut)
def register(user_in: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_in.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    upi_pin = None
    if user_in.role == "user":
        if user_in.upi_pin is None:
            conn.close()
            raise HTTPException(status_code=400, detail="UPI PIN is required for user accounts")
        if not (0 <= user_in.upi_pin <= 9999):
            conn.close()
            raise HTTPException(status_code=400, detail="UPI PIN must be a 4-digit number (0000-9999)")
        upi_pin = user_in.upi_pin
    
    hashed_pwd = hash_password(user_in.password)
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, phone, role, upi_pin) VALUES (?, ?, ?, ?, ?, ?)",
            (user_in.name, user_in.email, hashed_pwd, user_in.phone_number, user_in.role, upi_pin)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        new_user = {
            "id": user_id,
            "name": user_in.name,
            "email": user_in.email,
            "role": user_in.role,
            "phone_number": user_in.phone_number
        }
        return new_user
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()
