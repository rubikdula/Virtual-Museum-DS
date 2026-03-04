from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"User: {user.username}, Hash: {user.hashed_password}")
db.close()
