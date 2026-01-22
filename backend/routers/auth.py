from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from utils.db import supabase
from utils.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Pydantic Models ---
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    

# --- Endpoints ---

@router.post("/signup")
async def signup(user: UserSignup):
    try:
        existing_user = supabase.table("users").select("email").eq("email", user.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_pwd = get_password_hash(user.password)

        user_data = {
            "email": user.email,
            "password_hash": hashed_pwd,
            "full_name": user.full_name
        }
        response = supabase.table("users").insert(user_data).execute()
        
        user_id = response.data[0]['id']
        base_path = f"data/user_{user_id}"
        os.makedirs(f"{base_path}/documents", exist_ok=True)
        os.makedirs(f"{base_path}/vectorstore", exist_ok=True)

        return {"message": "User created successfully", "user_id": user_id}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    response = supabase.table("users").select("*").eq("email", user.email).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    user_db = response.data[0]

    if not verify_password(user.password, user_db['password_hash']):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user_db['email'], "user_id": user_db['id']},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}