from utils.security import get_password_hash, verify_password, create_access_token
from jose import jwt
import os

def test_password_hashing():
    password = "securepassword123"
    hashed = get_password_hash(password)
    
    # 1. Verify correct password works
    assert verify_password(password, hashed) is True
    
    # 2. Verify wrong password fails
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_generation():
    data = {"sub": "test@example.com", "user_id": "123"}
    token = create_access_token(data)
    
    # Decode to verify
    decoded = jwt.decode(
        token, 
        os.getenv("SECRET_KEY", "your-secret-key"), # Fallback if env not set in test
        algorithms=[os.getenv("ALGORITHM", "HS256")]
    )
    
    assert decoded["sub"] == "test@example.com"
    assert decoded["user_id"] == "123"