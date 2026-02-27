import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")