from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import shutil
import os
import uuid

from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/artifacts",
    tags=["artifacts"]
)

UPLOAD_DIR = "app/media"

@router.post("/create")
async def create_artifact(
    title: str = Form(...),
    short_description: str = Form(...),
    long_description: str = Form(None),
    year: str = Form(None),
    era: str = Form("Modern"),
    category: str = Form(...),
    tags: str = Form(None),
    media_type: str = Form(...), # "image", "video_url", "3d_url"
    media_url_input: str = Form(None), # For external links
    file: UploadFile = File(None), # For file uploads
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    final_media_url = media_url_input

    # Handle file upload if provided and media_type implies a file
    if (media_type == "image" or media_type == "3d_model") and file and file.filename:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        final_media_url = f"/media/{unique_filename}"
    
    new_artifact = models.Artifact(
        title=title,
        creator_id=current_user.id,
        short_description=short_description,
        long_description=long_description,
        year=year,
        era=era,
        category=category,
        tags=tags,
        media_type=media_type,
        media_url=final_media_url
    )
    
    db.add(new_artifact)
    db.commit()
    db.refresh(new_artifact)
    
    return RedirectResponse(url=f"/artifact/{new_artifact.id}", status_code=303)

@router.post("/{artifact_id}/delete")
async def delete_artifact(
    artifact_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
        
    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    if artifact.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this artifact")
        
    db.delete(artifact)
    db.commit()
    
    return RedirectResponse(url="/my-artifacts", status_code=303)

@router.post("/{artifact_id}/like")
async def like_artifact(
    artifact_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
         return RedirectResponse(url="/login?error=Please login to like artifacts", status_code=303)

    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Check if already liked
    existing_like = db.query(models.Like).filter(
        models.Like.user_id == current_user.id,
        models.Like.artifact_id == artifact_id
    ).first()

    if existing_like:
        # Already liked -> Unlike
        db.delete(existing_like)
        if artifact.likes_count > 0:
            artifact.likes_count -= 1
    else:
        # Not liked -> Like
        new_like = models.Like(user_id=current_user.id, artifact_id=artifact_id)
        db.add(new_like)
        artifact.likes_count += 1
    
    db.commit()
    
    # Redirect back to the artifact page
    return RedirectResponse(url=f"/artifact/{artifact_id}", status_code=303)
