import sqlite3
connection = sqlite3.connect("database.db")
cursor = connection.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS hymns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               category TEXT NOT NULL,
               audio TEXT,
               lyrics TEXT,
               favorite INTEGER DEFAULT 0
               )
               """)
try:
    cursor.execute("ALTER TABLE hymns ADD COLUMN favorite INTEGER DEFAULT 0")
except:
    pass
connection.commit()
connection.close()
print("Database created successfully")