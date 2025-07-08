from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.db.models import User
from app.db.connector import get_db
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional
from app.utils.jwt_utils import create_access_token
from app.utils.kafka_producer import send_event
from app.utils.redis_client import redis_client

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db=Depends(get_db)):
    # Check if user exists
    if db["users"].find_one({"$or": [{"username": user.username}, {"email": user.email}]}):
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    hashed_pw = hash_password(user.password)
    user_dict = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        created_at=datetime.utcnow()
    ).dict(by_alias=True)
    db["users"].insert_one(user_dict)
    # Send event to Kafka
    send_event("user-registrations", f"User {user.username} registered")
    # Optionally cache welcome message
    redis_client.setex(f"welcome:{user.username}", 600, "Welcome to AetherPulse!")
    return {"msg": "User registered successfully."}

@router.post("/login")
def login(user: UserLogin, db=Depends(get_db)):
    query = {"username": user.username} if user.username else {"email": user.email}
    db_user = db["users"].find_one(query)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token_data = {"sub": str(db_user["_id"]), "username": db_user["username"]}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"} 