import sqlite3
import os

db_path = 'hospital.db'
print(f"Database path: {os.path.abspath(db_path)}")
print(f"Database exists: {os.path.exists(db_path)}")
if os.path.exists(db_path):
    print(f"Database size: {os.path.getsize(db_path)} bytes")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [table[0] for table in cursor.fetchall()]
    print("Existing tables:", tables)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
