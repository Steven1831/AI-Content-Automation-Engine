
import os
import sqlite3
import re
import unicodedata
from pathlib import Path
from tools.utils.google_drive import GoogleDriveTool
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from flows.image_content_generator.pipeline.schemas import State

def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('_')

# Config
db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
# HARDCODED ID FROM .env to ensure it works
folder_id = "1siAr-Q39RUYdkFdS194HbKmYE_6_Iqg0"
store = SqliteStore(db_path)
drive = GoogleDriveTool()

print(f"--- Sincronizando Base de Datos con Drive (Carpeta: {folder_id}) ---")

# 1. Obtener todos los archivos de la carpeta de Drive
query = f"'{folder_id}' in parents and trashed = false"
results = drive.service.files().list(
    q=query,
    spaces='drive',
    fields='files(id, name)'
).execute()
drive_files = results.get('files', [])
print(f"Encontrados {len(drive_files)} archivos en Drive.")

# 2. Mapear nombres de archivos a IDs de Drive
drive_map = {f['name']: f['id'] for f in drive_files}

# 3. Actualizar la DB
ideas = store.get_all()
updated_count = 0

for idea in ideas:
    video_title_slug = slugify(idea.title if idea.title else f"video_{idea.id}")
    drive_name = f"{video_title_slug}.mp4"
    
    # Try multiple naming conventions
    possible_names = [
        drive_name,
        idea.title.lower().replace(" ", "_") + ".mp4",
        idea.title.lower().replace(" ", "-") + ".mp4",
        f"video_{idea.id}.mp4"
    ]
    
    found_id = None
    for name in possible_names:
        if name in drive_map:
            found_id = drive_map[name]
            break
            
    if found_id:
        if not idea.drive_file_id:
            idea.drive_file_id = found_id
            # Si ya tiene el archivo en Drive, nos aseguramos de que el estado sea al menos UPLOADED_TO_DRIVE
            if idea.state in [State.METADATA_GENERATED, State.VIDEO_SUBTITLED]:
                idea.state = State.UPLOADED_TO_DRIVE
            
            store.save(idea)
            print(f"SINCRO: ID {idea.id} ('{idea.title}') -> Drive ID {found_id}")
            updated_count += 1

print(f"\nSincronización terminada. {updated_count} ideas actualizadas.")
