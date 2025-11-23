from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models
import random
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/ai",
    tags=["AI Guide"]
)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.get("/generate_tour")
def generate_tour(era: str = None, db: Session = Depends(database.get_db)):
    """
    Generates a guided tour path through the museum using OpenAI to create a narrative.
    """
    
    # 1. Fetch artifacts
    query = db.query(models.Artifact)
    if era:
        query = query.filter(models.Artifact.era == era)
        
    # Get the list that matches what the frontend sees (for index calculation)
    all_artifacts_in_view = query.order_by(models.Artifact.likes_count.desc(), models.Artifact.id.asc()).all()
    
    # Select top 3 for the tour (to keep API costs/latency low)
    tour_artifacts = all_artifacts_in_view[:3]
    
    if not tour_artifacts:
        return {"tour": []}

    # 2. Prepare data for AI
    artifacts_info = []
    for i, art in enumerate(tour_artifacts):
        artifacts_info.append({
            "id": art.id,
            "title": art.title,
            "description": art.short_description,
            "index": i # We need this to map back to the correct position
        })

    # 3. Generate Narrative with OpenAI
    prompt = f"""
    You are a charismatic museum tour guide. Create a short, engaging tour script for a virtual museum visit in the '{era or 'General'}' era.
    
    The tour has {len(tour_artifacts)} stops.
    
    Artifacts to visit:
    {json.dumps(artifacts_info)}
    
    Please generate a JSON response with the following structure:
    {{
        "intro": "Welcome message...",
        "stops": [
            {{
                "artifact_id": 123,
                "script": "Narrative for this artifact..."
            }},
            ...
        ],
        "outro": "Goodbye message..."
    }}
    
    Keep the scripts concise (2-3 sentences per artifact). Be thematic to the era.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI guide. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        ai_content = json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"AI Tour Generation Error: {e}")
        # Fallback
        ai_content = {
            "intro": "Welcome to the tour. I am having trouble connecting to my brain, but follow me!",
            "stops": [{"artifact_id": a.id, "script": f"This is {a.title}."} for a in tour_artifacts],
            "outro": "Thank you for visiting."
        }

    tour_stops = []
    
    # Intro
    tour_stops.append({
        "type": "intro",
        "text": ai_content.get("intro", "Welcome!"),
        "duration": 5000
    })

    # Stops
    ai_stops_map = {s["artifact_id"]: s["script"] for s in ai_content.get("stops", [])}

    for art in tour_artifacts:
        try:
            real_index = all_artifacts_in_view.index(art)
        except ValueError:
            continue

        # Calculate position (matching museum_3d.html logic)
        side = -3 if real_index % 2 == 0 else 3
        z_pos = -real_index * 4
        
        # Target position for the player (standing in front of the art)
        stand_x = -1 if side == -3 else 1
        stand_z = z_pos + 1 
        
        tour_stops.append({
            "type": "stop",
            "artifact_id": art.id,
            "title": art.title,
            "text": ai_stops_map.get(art.id, f"Here is {art.title}."),
            "position": {"x": stand_x, "y": 0, "z": stand_z},
            "look_at": {"x": side, "y": 2, "z": z_pos},
            "duration": 8000
        })

    # Outro
    tour_stops.append({
        "type": "outro",
        "text": ai_content.get("outro", "Goodbye!"),
        "duration": 5000
    })

    return {"tour": tour_stops}
