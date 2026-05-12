
import os
import json
from datetime import datetime
from pathlib import Path
from tools.utils.youtube_uploader import YouTubeUploader
from tools.common.messenger import Messenger

SCHEDULE_FILE = Path("flows/image_content_generator/out_short/youtube_schedule.json")

def sync_schedule_with_youtube():
    yt = YouTubeUploader()
    Messenger.info("Consultando videos programados en YouTube...")
    
    try:
        # 1. Obtener videos (incluyendo privados y programados)
        request = yt.youtube.search().list(
            part="snippet",
            forMine=True,
            type="video",
            maxResults=50
        )
        response = request.execute()
        
        schedule_data = {}
        
        # 2. Obtener detalles de cada video para ver su fecha de publicación (publishAt)
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            details = yt.youtube.videos().list(
                part="status,snippet,liveStreamingDetails",
                id=video_id
            ).execute()
            
            for video in details.get('items', []):
                # Si el video tiene una fecha de publicación programada
                publish_at = video.get('status', {}).get('publishAt')
                if publish_at:
                    dt = datetime.fromisoformat(publish_at.replace('Z', '+00:00'))
                    date_str = dt.date().isoformat()
                    
                    if date_str not in schedule_data:
                        schedule_data[date_str] = []
                    
                    # Identificar si es mañana o tarde (para mantener compatibilidad)
                    hour = dt.hour
                    slot = "morning" if hour < 12 else "afternoon"
                    if slot not in schedule_data[date_str]:
                        schedule_data[date_str].append(slot)
                        Messenger.success(f"Slot detectado en YouTube: {date_str} {slot}")

        # 3. Guardar en el archivo local
        SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SCHEDULE_FILE.write_text(json.dumps(schedule_data, indent=2), encoding="utf-8")
        Messenger.info(f"Sincronización terminada. {len(schedule_data)} días registrados en el historial local.")

    except Exception as e:
        if "quotaExceeded" in str(e):
            Messenger.error("No se pudo sincronizar ahora mismo: CUOTA EXCEDIDA. Intenta de nuevo mañana.")
        else:
            Messenger.error(f"Error al sincronizar calendario: {e}")

if __name__ == "__main__":
    sync_schedule_with_youtube()
