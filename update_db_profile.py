import sqlite3

conn = sqlite3.connect('virtual_museum_v2.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR")
    print("Added full_name to users")
except Exception as e:
    print(f"Error adding full_name: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
    print("Added bio to users")
except Exception as e:
    print(f"Error adding bio: {e}")

conn.commit()
conn.close()
