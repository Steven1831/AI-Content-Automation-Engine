from enum import Enum
from typing import List

from pydantic import BaseModel


class State(str, Enum):
    NEW = "NEW"
    SCRIPT_GENERATED = "SCRIPT_GENERATED"
    SCRIPT_VALIDATED = "SCRIPT_VALIDATED"
    IMAGES_GENERATED = "IMAGES_GENERATED"
    VIDEOS_GENERATED = "VIDEOS_GENERATED"
    AUDIO_GENERATED = "AUDIO_GENERATED"
    VIDEO_GENERATED = "VIDEO_GENERATED"
    VIDEO_SUBTITLED = "VIDEO_SUBTITLED"
    VIDEO_MUSIC_GENERATED = "VIDEO_MUSIC_GENERATED"
    METADATA_GENERATED = "METADATA_GENERATED"
    UPLOADED_TO_DRIVE = "UPLOADED_TO_DRIVE"
    PUBLISHED_TO_YOUTUBE = "PUBLISHED_TO_YOUTUBE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class VideoOrientation(str, Enum):
    SHORT = "short"
    LONG = "long"


class SceneAlignment(BaseModel):
    scene_number: int
    start_time: float
    end_time: float


class AudioAlignment(BaseModel):
    alignments: List[SceneAlignment]


from typing import List, Optional

class IdeaRaw(BaseModel):
    id: int
    title: str
    state: State
    category: str
    drive_file_id: Optional[str] = None
    youtube_video_id: Optional[str] = None
