import sqlite3

conn = sqlite3.connect('virtual_museum_v2.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN museum_theme VARCHAR DEFAULT 'starry'")
    print("Added museum_theme to users")
except Exception as e:
    print(f"Error adding museum_theme: {e}")

try:
    cursor.execute("ALTER TABLE artifacts ADD COLUMN pos_x FLOAT DEFAULT 0.0")
    cursor.execute("ALTER TABLE artifacts ADD COLUMN pos_y FLOAT DEFAULT 2.0")
    cursor.execute("ALTER TABLE artifacts ADD COLUMN pos_z FLOAT DEFAULT 0.0")
    cursor.execute("ALTER TABLE artifacts ADD COLUMN rot_y FLOAT DEFAULT 0.0")
    cursor.execute("ALTER TABLE artifacts ADD COLUMN is_placed BOOLEAN DEFAULT 0")
    print("Added position columns to artifacts")
except Exception as e:
    print(f"Error adding artifact columns: {e}")

conn.commit()
conn.close()
