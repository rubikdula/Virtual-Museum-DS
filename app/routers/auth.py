from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from .. import models, schemas, database
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto") 

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey") # Fallback for dev, but should be in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Remove "Bearer " prefix if present (though we set it directly)
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(models.User).filter(models.User.username == username).first()
    return user

@router.post("/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        # In a real app, show error on the form
        return RedirectResponse(url="/signup?error=Username already registered", status_code=303)
    
    hashed_password = get_password_hash(password)
    new_user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto login after signup
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/profile/edit")
async def edit_profile_page(request: Request, current_user: models.User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": current_user})

@router.post("/profile/edit")
async def update_profile(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(None),
    bio: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Check if username is taken (if changed)
    if username != current_user.username:
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            # Ideally return to form with error
            return RedirectResponse(url="/auth/profile/edit?error=Username taken", status_code=303)
    
    current_user.username = username
    current_user.email = email
    current_user.full_name = full_name
    current_user.bio = bio
    
    db.commit()
    
    # If username changed, we need to update the token!
    # For simplicity, let's just update the cookie with a new token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/my-artifacts", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return response
