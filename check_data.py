from app import models, database
from app.database import SessionLocal

db = SessionLocal()
artifacts = db.query(models.Artifact).all()
for art in artifacts:
    print(f"Title: {art.title}, Era: {art.era}")
