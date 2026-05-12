import sqlite3
import json

conn = sqlite3.connect(r'c:\Users\steven.ventura\Downloads\contenido ai\AI-Content-Automation-Engine\flows\image_content_generator\out_short\ideas_tracking.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT id, title, state FROM ideas WHERE state IN ("COMPLETED", "ARCHIVED") ORDER BY id ASC')
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row['id']} - Título: {row['title']} ({row['state']})")
