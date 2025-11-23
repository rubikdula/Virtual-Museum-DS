from app.database import engine, Base
from app.models import Collection

print("Creating collection table...")
Base.metadata.create_all(bind=engine)
print("Done!")
