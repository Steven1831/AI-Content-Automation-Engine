
import os
import io
import sqlite3
from pathlib import Path
from googleapiclient.http import MediaIoBaseDownload
from tools.utils.google_drive import GoogleDriveTool
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from flows.image_content_generator.pipeline.schemas import State
from tools.common.messenger import Messenger

# Config
db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
store = SqliteStore(db_path)
drive = GoogleDriveTool()

def rescue_video(idea_obj):
    try:
        idea_path = Path(f"flows/image_content_generator/out_short/ideas/idea_{idea_obj.id:06d}")
        editions_path = idea_path / "editions"
        editions_path.mkdir(parents=True, exist_ok=True)
        
        video_path = editions_path / "final_video_subtitled_music.mp4"
        
        if not video_path.exists():
            Messenger.info(f"Descargando video para ID {idea_obj.id} desde Drive...")
            request = drive.service.files().get_media(fileId=idea_obj.drive_file_id)
            fh = io.FileIO(video_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Progreso: {int(status.progress() * 100)}%", end='\r')
            Messenger.success(f"Video ID {idea_obj.id} restaurado localmente.")
        return True
    except Exception as e:
        Messenger.error(f"Error rescatando ID {idea_obj.id}: {e}")
        return False

# Procesar los que están en UPLOADED_TO_DRIVE pero no tienen carpeta
ideas = store.get_all_by_state(State.UPLOADED_TO_DRIVE, limit=50)
for idea in ideas:
    rescue_video(idea)

print("\nRescate completado. El loop de producción ahora podrá publicarlos.")
