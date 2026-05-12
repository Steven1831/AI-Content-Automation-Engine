
import sqlite3
import pandas as pd

conn = sqlite3.connect('flows/image_content_generator/out_short/ideas_tracking.db')
query = "SELECT id, title, state FROM ideas WHERE state != 'ARCHIVED' ORDER BY id DESC LIMIT 30"
df = pd.read_sql_query(query, conn)

print("\n--- ESTADO ACTUAL DE LA COLA DE PRODUCCIÓN ---")
print(df.to_string(index=False))
conn.close()
