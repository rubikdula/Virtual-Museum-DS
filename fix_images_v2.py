from app.database import SessionLocal
from app import models

db = SessionLocal()

updates = [
    {
        "title": "Apollo 11 Command Module",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Apollo_11_Command_module_Columbia.jpg/800px-Apollo_11_Command_module_Columbia.jpg"
    },
    {
        "title": "Wright Flyer",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/First_flight2.jpg/1200px-First_flight2.jpg"
    },
    {
        "title": "First Transistor",
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Replica-of-first-transistor.jpg"
    }
]

for item in updates:
    artifact = db.query(models.Artifact).filter(models.Artifact.title == item["title"]).first()
    if artifact:
        print(f"Updating {artifact.title}...")
        artifact.media_url = item["url"]
    else:
        print(f"Artifact {item['title']} not found.")

db.commit()
print("Database updated successfully.")
db.close()
