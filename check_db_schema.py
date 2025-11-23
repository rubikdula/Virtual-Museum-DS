from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('artifacts')
for column in columns:
    print(column['name'], column['type'])
