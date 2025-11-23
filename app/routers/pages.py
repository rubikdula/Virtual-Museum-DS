from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse # <--- Added HTMLResponse here
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .. import models, database
from .auth import get_current_user

router = APIRouter(
    tags=["pages"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(
    request: Request, 
    search: str = None, 
    category: str = None,
    era: str = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Artifact)
    
    if search:
        search_filter = or_(
            models.Artifact.title.ilike(f"%{search}%"),
            models.Artifact.tags.ilike(f"%{search}%"),
            models.Artifact.category.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if category:
        query = query.filter(models.Artifact.category == category)

    if era:
        query = query.filter(models.Artifact.era == era)
        
    artifacts = query.order_by(models.Artifact.created_at.desc()).all()
    
    # Get unique categories for filter dropdown
    categories = db.query(models.Artifact.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    liked_artifact_ids = []
    if current_user:
        likes = db.query(models.Like).filter(models.Like.user_id == current_user.id).all()
        liked_artifact_ids = [like.artifact_id for like in likes]
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "artifacts": artifacts, 
        "user": current_user,
        "search": search,
        "categories": categories,
        "selected_era": era,
        "liked_artifact_ids": liked_artifact_ids
    })

@router.get("/artifact/{artifact_id}")
async def artifact_detail(
    request: Request, 
    artifact_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not artifact:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Artifact not found", "user": current_user})
    
    # Increment view count
    artifact.views_count += 1
    db.commit()
    
    is_liked = False
    collection_status = "none" # none, pending, approved

    if current_user:
        existing_like = db.query(models.Like).filter(
            models.Like.user_id == current_user.id,
            models.Like.artifact_id == artifact_id
        ).first()
        if existing_like:
            is_liked = True
            
        # Check collection status
        collection_entry = db.query(models.Collection).filter(
            models.Collection.user_id == current_user.id,
            models.Collection.artifact_id == artifact_id
        ).first()
        
        if collection_entry:
            if collection_entry.is_approved:
                collection_status = "approved"
            else:
                collection_status = "pending"

    return templates.TemplateResponse("artifact_detail.html", {
        "request": request, 
        "artifact": artifact, 
        "user": current_user,
        "is_liked": is_liked,
        "collection_status": collection_status
    })

@router.get("/upload")
async def upload_page(
    request: Request, 
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please login to upload"})
        
    return templates.TemplateResponse("upload_artifact.html", {"request": request, "user": current_user})

@router.get("/my-artifacts")
async def my_artifacts(
    request: Request, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})
        
    artifacts = db.query(models.Artifact).filter(models.Artifact.creator_id == current_user.id).all()
    
    return templates.TemplateResponse("my_artifacts.html", {
        "request": request, 
        "artifacts": artifacts, 
        "user": current_user
    })

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# 1. The Route to view the 3D world
@router.get("/world", response_class=HTMLResponse)
def world_3d(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_likes = 0
    username = "Guest"
    
    if current_user:
        username = current_user.username
        # Calculate total likes received on all their artifacts
        user_artifacts = db.query(models.Artifact).filter(models.Artifact.creator_id == current_user.id).all()
        total_likes = sum(a.likes_count for a in user_artifacts)
        
    return templates.TemplateResponse("museum_3d.html", {
        "request": request, 
        "user": current_user,
        "username": username,
        "total_likes": total_likes
    })

# 2. A JSON endpoint for the JS to fetch artifact data
@router.get("/artifacts_json")
def get_artifacts_json(
    era: str = None,
    db: Session = Depends(database.get_db)
):
    # Fetch all artifacts, sorted by likes_count descending
    query = db.query(models.Artifact)
    
    if era:
        query = query.filter(models.Artifact.era == era)
        
    artifacts = query.order_by(models.Artifact.likes_count.desc(), models.Artifact.id.asc()).all()
    # Convert to simple list of dicts
    data = []
    for art in artifacts:
        data.append({
            "id": art.id,
            "title": art.title,
            "media_url": art.media_url if art.media_url else "https://via.placeholder.com/300",
            "likes": art.likes_count,
            "description": art.short_description,
            "era": art.era
        })
    return JSONResponse(content=data)

@router.get("/notifications")
async def notifications_page(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    notifications = db.query(models.Notification)\
        .filter(models.Notification.recipient_id == current_user.id)\
        .order_by(models.Notification.created_at.desc())\
        .all()
    
    # Mark all as read
    for notif in notifications:
        notif.is_read = True
    db.commit()
    
    return templates.TemplateResponse("notifications.html", {
        "request": request,
        "user": current_user,
        "notifications": notifications
    })
