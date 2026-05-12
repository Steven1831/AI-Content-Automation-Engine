
import os
import sqlite3
from pathlib import Path
from tools.utils.youtube_uploader import YouTubeUploader
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from flows.image_content_generator.pipeline.schemas import State
from tools.common.messenger import Messenger

# Config
db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
store = SqliteStore(db_path)
yt = YouTubeUploader()

print(f"{'ID':<4} | {'ESTADO':<20} | {'DRIVE':<8} | {'YOUTUBE':<12} | {'TITULO'}")
print("-" * 80)

try:
    # Obtener videos de YouTube para cruzar datos
    request = yt.youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        maxResults=50
    )
    response = request.execute()
    yt_titles = [item['snippet']['title'].strip().lower() for item in response.get('items', [])]

    ideas = {i.id: i for i in store.get_all()}
    
    for i in range(1, 40):
        idea = ideas.get(i)
        if not idea:
            continue
            
        on_drive = "SI" if idea.drive_file_id else "NO"
        
        # Check YT by ID or by title match
        on_yt = "NO"
        if idea.youtube_video_id:
            on_yt = "SI (ID)"
        else:
            idea_title_lower = idea.title.strip().lower()
            for yt_title in yt_titles:
                if idea_title_lower in yt_title or yt_title in idea_title_lower:
                    on_yt = "SI (MATCH)"
                    break
        
        print(f"{idea.id:<4} | {idea.state.value:<20} | {on_drive:<8} | {on_yt:<12} | {idea.title}")

except Exception as e:
    print(f"Error generando reporte: {e}")
