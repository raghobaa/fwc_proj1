from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from src.config.auth import create_access_token, get_current_user, TokenData

router = APIRouter()

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or customer ID")
    password: str = Field(..., description="Password")

# For demo purposes, we use a hard‑coded user store. In production replace with DB lookup.
FAKE_USERS_DB = {
    "C-101": {
        "username": "C-101",
        "hashed_password": "${hashed_password_placeholder}",  # placeholder; replace with real hash
        "role": "customer",
    },
    "admin": {
        "username": "admin",
        "hashed_password": "${hashed_password_placeholder}",
        "role": "admin",
    },
}

@router.post("/login")
async def login(req: LoginRequest):
    user = FAKE_USERS_DB.get(req.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    # In a real app, verify password using the pwd_context from src.config.auth
    # Here we skip password verification for brevity.
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def read_me(current_user: TokenData = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}
