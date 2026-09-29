from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from src.config.auth import create_access_token, get_current_user, TokenData

router = APIRouter()

class LoginRequest(BaseModel):
    email: str  # user's email address

# Role is derived from the email address:
#   - admin@trendly.com  → admin
#   - agent@trendly.com  → agent
#   - anything else      → customer
def role_from_email(email: str) -> str:
    email = email.lower().strip()
    if email == "admin@trendly.com":
        return "admin"
    if email == "agent@trendly.com":
        return "agent"
    return "customer"

@router.post("/login")
async def login(req: LoginRequest):
    email = req.email.lower().strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address")
    role = role_from_email(email)
    token = create_access_token({"sub": email, "role": role})
    return {"access_token": token, "token_type": "bearer", "role": role}

@router.get("/me")
async def read_me(current_user: TokenData = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}
