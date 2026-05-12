import os
import pickle
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tools.common.messenger import Messenger

class YouTubeUploader:
    """
    Handles YouTube video uploads and scheduling.
    """
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    TOKEN_FILE = 'youtube_token.pickle'
    CREDENTIALS_FILE = 'credentials.json'

    def __init__(self):
        self.youtube = self._get_service()

    def _get_service(self):
        creds = None
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                # We disable automatic browser opening to allow remote authentication
                creds = flow.run_local_server(port=0, open_browser=False, prompt='consent')
            
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def check_if_video_exists(self, title: str) -> Optional[str]:
        """Checks if a video with the same title already exists in the channel."""
        try:
            request = self.youtube.search().list(
                part="snippet",
                forMine=True,
                q=title,
                type="video",
                maxResults=5
            )
            response = request.execute()
            for item in response.get('items', []):
                if item['snippet']['title'].strip().lower() == title.strip().lower():
                    return item['id']['videoId']
        except Exception as e:
            Messenger.warning(f"Error al verificar duplicados en YouTube: {e}")
        return None

    def upload_video(self, file_path, title, description, tags=None, publish_at=None):
        """
        Uploads a video to YouTube.
        If publish_at is provided (datetime), it schedules the video.
        """
        # Check for duplicates first
        existing_id = self.check_if_video_exists(title)
        if existing_id:
            Messenger.warning(f"El video '{title}' ya existe en YouTube (ID: {existing_id}). Saltando subida.")
            return existing_id

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': '22' # People & Blogs
            },
            'status': {
                'privacyStatus': 'private', # Default to private for scheduling
                'selfDeclaredMadeForKids': False
            }
        }

        if publish_at:
            # Ensure publish_at is timezone-aware (local timezone)
            import datetime
            if publish_at.tzinfo is None:
                # Assume system local timezone
                publish_at = publish_at.replace(tzinfo=datetime.datetime.now().astimezone().tzinfo)
            # Convert to UTC
            utc_publish_at = publish_at.astimezone(datetime.timezone.utc)
            # Ensure the scheduled time is in the future (YouTube requires > now)
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            if utc_publish_at <= now_utc:
                # If the time is in the past, push it to the next available slot (add 1 day)
                utc_publish_at = utc_publish_at + datetime.timedelta(days=1)
            body['status']['publishAt'] = utc_publish_at.isoformat(timespec='seconds').replace('+00:00', 'Z')
            body['status']['privacyStatus'] = 'private'  # Must be private to schedule

        Messenger.info(f"Subiendo a YouTube: {title}...")
        
        media = MediaFileUpload(
            file_path,
            mimetype='video/mp4',
            resumable=True
        )

        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                Messenger.info(f"Progreso subida: {int(status.progress() * 100)}%")

        Messenger.success(f"Video subido con exito! ID: {response['id']}")
        return response['id']
