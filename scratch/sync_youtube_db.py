
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

print("--- Sincronizando Base de Datos con Canal de YouTube ---")

try:
    # 1. Obtener los videos del canal (últimos 50)
    request = yt.youtube.search().list(
        part="snippet",
        forMine=True,
        type="video",
        maxResults=50
    )
    response = request.execute()
    yt_titles = [item['snippet']['title'].strip().lower() for item in response.get('items', [])]
    Messenger.info(f"Encontrados {len(yt_titles)} videos en el canal.")

    # 2. Comparar con la DB
    ideas = store.get_all()
    updated_count = 0

    for idea in ideas:
        # Check if title or slug matches any YT title
        match = False
        idea_title_lower = idea.title.strip().lower()
        
        for yt_title in yt_titles:
            if idea_title_lower in yt_title or yt_title in idea_title_lower:
                match = True
                break
        
        if match:
            if idea.state != State.ARCHIVED:
                idea.state = State.ARCHIVED
                store.save(idea)
                Messenger.success(f"SINCRO YT: ID {idea.id} ('{idea.title}') ya est en YouTube. Marcado como ARCHIVADO.")
                updated_count += 1

    print(f"\nSincronizacin terminada. {updated_count} ideas marcadas como ya publicadas.")

except Exception as e:
    Messenger.error(f"Error sincronizando con YouTube: {e}")
