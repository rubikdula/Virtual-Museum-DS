from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database
import openai
import os
import numpy as np
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"]
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple in-memory cache for embeddings: {artifact_id: embedding_vector}
embedding_cache = {}

def get_embedding(text: str):
    # Normalize text
    text = text.replace("\n", " ")
    # Use a small, efficient model
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

@router.get("/enrich/{artifact_id}")
def enrich_artifact(artifact_id: int, db: Session = Depends(database.get_db)):
    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    # 1. Generate Fact Check / Knowledge Expansion
    prompt = f"""
    Analyze the following artifact:
    Title: {artifact.title}
    Era: {artifact.era}
    Description: {artifact.long_description}

    Please provide:
    1. Two related inventions that led to this or resulted from this.
    2. One interesting historical connection or fact.
    
    Format the output as JSON with keys: "related_inventions" (list of strings), "historical_connection" (string).
    """

    ai_data = {"related_inventions": [], "historical_connection": "AI analysis unavailable."}

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable museum curator AI. Output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        content = completion.choices[0].message.content
        ai_data = json.loads(content)
    except Exception as e:
        print(f"OpenAI Generation Error: {e}")
        # Fallback if JSON parsing fails or API fails
        ai_data["historical_connection"] = f"Error generating analysis: {str(e)}"

    # 2. Find Similar Artifacts using Embeddings
    similar_artifacts_data = []
    try:
        # Fetch all artifacts to compare
        all_artifacts = db.query(models.Artifact).all()
        
        # Ensure current artifact is in cache
        current_text = f"{artifact.title} {artifact.long_description}"
        if artifact.id not in embedding_cache:
            embedding_cache[artifact.id] = get_embedding(current_text)
        
        current_vec = embedding_cache[artifact.id]
        
        similarities = []
        for other in all_artifacts:
            if other.id == artifact.id:
                continue
                
            if other.id not in embedding_cache:
                other_text = f"{other.title} {other.long_description}"
                try:
                    embedding_cache[other.id] = get_embedding(other_text)
                except Exception as e:
                    print(f"Embedding Error for {other.id}: {e}")
                    continue
            
            other_vec = embedding_cache[other.id]
            score = cosine_similarity(current_vec, other_vec)
            similarities.append((score, other))
        
        # Sort by score desc
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_3 = similarities[:3]
        
        similar_artifacts_data = [
            {
                "id": a.id,
                "title": a.title,
                "era": a.era,
                "similarity": float(score)
            }
            for score, a in top_3
        ]
    except Exception as e:
        print(f"Similarity Search Error: {e}")

    return {
        "artifact_id": artifact.id,
        "ai_analysis": ai_data,
        "similar_artifacts": similar_artifacts_data
    }
