
import sqlite3
conn = sqlite3.connect('flows/image_content_generator/out_short/ideas_tracking.db')
conn.execute("UPDATE ideas SET state = 'ARCHIVED' WHERE id IN (30, 33)")
conn.commit()
print('IDs 30 y 33 archivados correctamente.')
