from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import shutil
import os
import uuid
import requests
import urllib.parse
from fastapi.templating import Jinja2Templates
import openai

from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/artifacts",
    tags=["artifacts"]
)

UPLOAD_DIR = "app/media"
templates = Jinja2Templates(directory="app/templates")

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
    request: Request,
    artifact_id: int,
    redirect_to: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        if request.headers.get("accept") == "application/json":
            raise HTTPException(status_code=401, detail="Login required")
        return RedirectResponse(url="/login?error=Please login to like artifacts", status_code=303)

    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Check if already liked
    existing_like = db.query(models.Like).filter(
        models.Like.user_id == current_user.id,
        models.Like.artifact_id == artifact_id
    ).first()

    is_liked = False
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
        is_liked = True

        # Create Notification
        if artifact.creator_id != current_user.id:
            notification = models.Notification(
                recipient_id=artifact.creator_id,
                sender_id=current_user.id,
                artifact_id=artifact.id,
                type="like",
                message=f"{current_user.username} liked your artifact '{artifact.title}'"
            )
            db.add(notification)
    
    db.commit()
    
    if request.headers.get("accept") == "application/json":
        return {"success": True, "likes_count": artifact.likes_count, "liked": is_liked}

    # Redirect back
    if redirect_to:
        return RedirectResponse(url=redirect_to, status_code=303)
    return RedirectResponse(url=f"/artifact/{artifact_id}", status_code=303)

@router.post("/{artifact_id}/comment")
async def create_comment(
    artifact_id: int,
    text: str = Form(...),
    redirect_to: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    new_comment = models.Comment(
        artifact_id=artifact_id,
        user_id=current_user.id,
        text=text
    )
    db.add(new_comment)

    # Create Notification
    if artifact.creator_id != current_user.id:
        notification = models.Notification(
            recipient_id=artifact.creator_id,
            sender_id=current_user.id,
            artifact_id=artifact.id,
            type="comment",
            message=f"{current_user.username} commented: {text[:30]}..."
        )
        db.add(notification)

    db.commit()
    
    if redirect_to:
        return RedirectResponse(url=redirect_to, status_code=303)
    return RedirectResponse(url=f"/artifact/{artifact_id}", status_code=303)

@router.post("/{artifact_id}/collect")
async def collect_artifact(
    artifact_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    original = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Artifact not found")

    # Prevent collecting own artifacts (optional, but makes sense to avoid duplicates)
    if original.creator_id == current_user.id:
        # Just redirect back with a message? For now just redirect.
        return RedirectResponse(url=f"/artifact/{artifact_id}", status_code=303)

    # Create a copy
    new_copy = models.Artifact(
        title=original.title,
        creator_id=current_user.id, # Now owned by the collector
        short_description=original.short_description,
        long_description=original.long_description,
        year=original.year,
        era=original.era,
        category=original.category,
        tags=f"{original.tags or ''}, Collected",
        media_type=original.media_type,
        media_url=original.media_url,
        is_placed=False, # Goes to inventory
        pos_x=0, pos_y=2, pos_z=0, rot_y=0
    )
    
    db.add(new_copy)
    db.commit()
    
    # Redirect to inventory or stay on page?
    # Let's redirect to My Collection to show it's there
    return RedirectResponse(url="/my-artifacts", status_code=303)

@router.get("/create-ai")
async def create_ai_page(request: Request, current_user: models.User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("create_ai_artifact.html", {"request": request, "user": current_user})

@router.post("/generate-ai")
async def generate_ai_artifact(
    prompt: str = Form(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    # 1. Generate Metadata using OpenAI
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = """
    You are a creative museum curator. Based on the user's prompt, create a fictional but plausible museum artifact entry.
    Return a JSON object with the following keys:
    - title: A catchy title for the artifact.
    - short_description: A 1-sentence summary.
    - long_description: A detailed 3-paragraph history/description.
    - year: The approximate year of origin (can be future).
    - era: One of [Ancient, Medieval, Industrial, Modern, Future].
    - category: One of [Art, Technology, Science, History, Magic].
    - tags: Comma-separated tags.
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create an artifact based on this idea: {prompt}"}
            ],
            response_format={ "type": "json_object" }
        )
        import json
        metadata = json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Metadata Generation Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate artifact metadata")

    # 2. Generate Image using Pollinations.ai
    # Enhance prompt for better image results
    image_prompt = f"{prompt}, {metadata['category']}, {metadata['era']} style, highly detailed, museum photography, 8k, cinematic lighting"
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    # Download and save image
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            unique_filename = f"ai_{uuid.uuid4()}.jpg"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
            final_media_url = f"/media/{unique_filename}"
        else:
            raise Exception("Image download failed")
    except Exception as e:
        print(f"Image Generation Error: {e}")
        # Fallback to the URL directly if download fails
        final_media_url = image_url

    # 3. Save to Database
    new_artifact = models.Artifact(
        title=metadata.get("title", "Unknown Artifact"),
        creator_id=current_user.id,
        short_description=metadata.get("short_description", ""),
        long_description=metadata.get("long_description", ""),
        year=metadata.get("year", "Unknown"),
        era=metadata.get("era", "Modern"),
        category=metadata.get("category", "Technology"),
        tags=f"AI Generated, {metadata.get('tags', '')}",
        media_type="image",
        media_url=final_media_url,
        is_placed=False # User needs to place it manually
    )
    
    db.add(new_artifact)
    db.commit()
    db.refresh(new_artifact)
    
    return RedirectResponse(url=f"/artifact/{new_artifact.id}", status_code=303)
