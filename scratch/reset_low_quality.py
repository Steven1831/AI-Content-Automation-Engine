
import os
import shutil
import sqlite3
from pathlib import Path

conn = sqlite3.connect('flows/image_content_generator/out_short/ideas_tracking.db')
ids = [8, 26, 31, 32, 34, 35, 37, 38]

print(f"Reseteando {len(ids)} videos para mejora de calidad...")

for id_num in ids:
    # 1. Reset state in DB
    conn.execute("UPDATE ideas SET state = 'NEW', drive_file_id = NULL, youtube_video_id = NULL WHERE id = ?", (id_num,))
    
    # 2. Delete local folder
    folder = Path(f"flows/image_content_generator/out_short/ideas/idea_{id_num:06d}")
    if folder.exists():
        shutil.rmtree(folder)
        print(f"Eliminado: {folder}")

conn.commit()
print(f"SINCRO: IDs {ids} reseteados exitosamente. Listos para re-generación de alta calidad.")
