
import sqlite3

conn = sqlite3.connect('flows/image_content_generator/out_short/ideas_tracking.db')
conn.execute("UPDATE ideas SET state = 'ARCHIVED' WHERE id IN (30, 33)")
conn.commit()
conn.close()
print("SINCRO FINAL: IDs 30 y 33 han sido archivados. El bot ya no los procesará.")
