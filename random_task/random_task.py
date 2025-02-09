from fastapi import FastAPI, Depends, HTTPException
import random
from pydantic import BaseModel
import bcrypt
from database.repository import UserRepository
from database.orm import User

app = FastAPI()

@app.get("/random_value")
def get_random_value():
    random_number = random.randint(0, 100)
    return {"random_value": random_number}

class SignUpRequest(BaseModel):
    username: str
    password: str

class LogInRequest(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

@app.post("/sign-up", status_code=201)
def sign_up(
    request: SignUpRequest,
    user_repo: UserRepository = Depends()
):
    # 이미 존재하는 사용자인지 확인
    if user_repo.get_user_by_username(request.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # 비밀번호 해싱
    hashed_password = hash_password(request.password)
    
    # 사용자 생성 및 저장
    user = User.create(
        username=request.username,
        hashed_password=hashed_password
    )
    user = user_repo.save_user(user)
    
    return {"id": user.id, "username": user.username}

@app.post("/log-in")
def log_in(
    request: LogInRequest,
    user_repo: UserRepository = Depends()
):
    user = user_repo.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return {"message": "Login successful"}

@app.get("/user/{username}")
def get_user(
    username: str,
    user_repo: UserRepository = Depends()
):
    user = user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user.id, "username": user.username}

@app.get("/users", status_code=200)
def get_all_users(
    user_repo: UserRepository = Depends()
):
    users = user_repo.get_all_users()
    return {"users": [{"id": user.id, "username": user.username} for user in users]}
