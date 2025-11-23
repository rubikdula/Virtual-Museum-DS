from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, database
from .auth import get_current_user
from typing import List, Dict

router = APIRouter(
    prefix="/museum",
    tags=["Personal Museum"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/{username}", response_class=HTMLResponse)
def personal_museum(
    request: Request,
    username: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    target_user = db.query(models.User).filter(models.User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    is_owner = False
    if current_user and current_user.id == target_user.id:
        is_owner = True
        
    return templates.TemplateResponse("museum_3d.html", {
        "request": request,
        "user": current_user,
        "username": current_user.username if current_user else "Guest",
        "target_username": target_user.username,
        "is_owner": is_owner,
        "mode": "personal",
        "theme": target_user.museum_theme
    })

@router.get("/api/{username}/artifacts")
def get_personal_artifacts(
    username: str,
    db: Session = Depends(database.get_db)
):
    target_user = db.query(models.User).filter(models.User.username == username).first()
    if not target_user:
        return []
        
    artifacts = db.query(models.Artifact).filter(
        models.Artifact.creator_id == target_user.id,
        models.Artifact.is_placed == True
    ).all()
    
    data = []
    for art in artifacts:
        data.append({
            "id": art.id,
            "title": art.title,
            "media_url": art.media_url,
            "likes": art.likes_count,
            "description": art.short_description,
            "position": {"x": art.pos_x, "y": art.pos_y, "z": art.pos_z},
            "rotation": {"y": art.rot_y}
        })
    return JSONResponse(content=data)

@router.get("/api/{username}/inventory")
def get_inventory(
    username: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only owner can see inventory to place items
    if not current_user or current_user.username != username:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    artifacts = db.query(models.Artifact).filter(
        models.Artifact.creator_id == current_user.id,
        models.Artifact.is_placed == False
    ).all()
    
    data = []
    for art in artifacts:
        data.append({
            "id": art.id,
            "title": art.title,
            "media_url": art.media_url
        })
    return JSONResponse(content=data)

@router.post("/api/update_layout")
async def update_layout(
    data: Dict = Body(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
        
    # data = { "artifact_id": 1, "position": {x,y,z}, "rotation": {y}, "is_placed": true }
    art_id = data.get("artifact_id")
    artifact = db.query(models.Artifact).filter(models.Artifact.id == art_id).first()
    
    if not artifact or artifact.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if "position" in data:
        artifact.pos_x = data["position"]["x"]
        artifact.pos_y = data["position"]["y"]
        artifact.pos_z = data["position"]["z"]
        
    if "rotation" in data:
        artifact.rot_y = data["rotation"]["y"]
        
    if "is_placed" in data:
        artifact.is_placed = data["is_placed"]
        
    db.commit()
    return {"status": "success"}

@router.post("/api/update_theme")
async def update_theme(
    data: Dict = Body(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
        
    theme = data.get("theme")
    current_user.museum_theme = theme
    db.commit()
    return {"status": "success"}
