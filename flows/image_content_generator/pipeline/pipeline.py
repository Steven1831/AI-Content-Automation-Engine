from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, ClassVar, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, PrivateAttr

from flows.image_content_generator.pipeline.prompt_base.models import VideoScript
from flows.image_content_generator.pipeline.prompt_longs.manager import PromptManagerLongs
from flows.image_content_generator.pipeline.prompt_shorts.manager import PromptManagerShorts
from flows.image_content_generator.pipeline.schemas import AudioAlignment, State, VideoOrientation
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from tools.audio_generation.audio_tool import AudioTool
from tools.audio_generation.gemini import GeminiAudioGenerator
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger
from tools.image_generation.gemini import GeminiImageGenerator
from tools.image_generation.midjourney import ImageTask
from tools.video_generation.gemini_veo import GeminiVideoGenerator
from tools.text_generation.gemini import GeminiTextGenerator
from tools.utils.text import slugify
from tools.utils.time import retry
from tools.video_editing.ffmpeg import FFmpegTool
from tools.video_editing.whisper import WhisperTool
from tools.text_generation.seo_prompts import SeoPromptManager
from tools.utils.google_drive import GoogleDriveTool
from tools.utils.youtube_uploader import YouTubeUploader
from tools.utils.scheduler import YouTubeScheduler

T = TypeVar("T", bound=BaseModel)
PromptManager = Union[PromptManagerShorts, PromptManagerLongs]


class Pipeline(BaseModelTool):
    """
    Main pipeline for the Image Content Generator project.
    Orchestrates the creation of shorts using AI tools (Gemini + Veo).
    """
    out_base: Path
    resource_base: Path
    orientation: VideoOrientation

    _text_gen: Optional[GeminiTextGenerator] = PrivateAttr(default=None)
    _image_gen: Optional[GeminiImageGenerator] = PrivateAttr(default=None)
    _video_gen: Optional[GeminiVideoGenerator] = PrivateAttr(default=None)
    _audio_gen: Optional[GeminiAudioGenerator] = PrivateAttr(default=None)
    _ffmpeg: Optional[FFmpegTool] = PrivateAttr(default=None)
    _whisper: Optional[WhisperTool] = PrivateAttr(default=None)
    _prompt_manager: Optional[PromptManager] = PrivateAttr(default=None)
    _audio_tool: Optional[AudioTool] = PrivateAttr(default=None)
    _store: Optional[SqliteStore] = PrivateAttr(default=None)
    _google_drive: Optional[GoogleDriveTool] = PrivateAttr(default=None)
    _youtube_uploader: Optional[YouTubeUploader] = PrivateAttr(default=None)

    # Standard Output Directories
    IDEAS_DIR: ClassVar[str] = "ideas"
    IMAGES_DIR: ClassVar[str] = "images"
    AUDIOS_DIR: ClassVar[str] = "audios"
    VIDEOS_DIR: ClassVar[str] = "videos"
    EDITIONS_DIR: ClassVar[str] = "editions"

    # Standard Output Files
    IDEA_JSON: ClassVar[str] = "idea.json"
    SCRIPT_JSON: ClassVar[str] = "script.json"
    RAW_VIDEO: ClassVar[str] = "raw_video.mp4"
    SUBTITLED_VIDEO: ClassVar[str] = "subtitled_video.mp4"
    FINAL_AUDIO: ClassVar[str] = "final_audio.wav"
    FINAL_SUBS: ClassVar[str] = "final_subs.srt"
    FINAL_VIDEO: ClassVar[str] = "final_video.mp4"
    SEO_METADATA_JSON: ClassVar[str] = "seo_metadata.json"

    # Standard Scene Patterns
    SCENE_IMAGE_PATTERN: ClassVar[str] = "scene_{}.png"
    SCENE_AUDIO_PATTERN: ClassVar[str] = "scene_{}.wav"
    SCENE_VIDEO_PATTERN: ClassVar[str] = "scene_{}.mp4"
    BATCH_AUDIO_PATTERN: ClassVar[str] = "batch_{}.wav"

    # Standard Resource Directories
    BG_MUSIC_DIR: ClassVar[str] = "bg-music"
    REFERENCES_DIR: ClassVar[str] = "reference"

    # Standard Tracking Files
    IDEAS_TRACKING_DB: ClassVar[str] = "ideas_tracking.db"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def store(self) -> SqliteStore:
        if self._store is None:
            db_path = self.out_base / self.IDEAS_TRACKING_DB
            self._store = SqliteStore(db_path=db_path)
        return self._store

    @property
    def text_gen(self) -> GeminiTextGenerator:
        if self._text_gen is None:
            self._text_gen = GeminiTextGenerator()
        return self._text_gen

    @property
    def image_gen(self) -> GeminiImageGenerator:
        if self._image_gen is None:
            ar_value = "9:16" if self.orientation == VideoOrientation.SHORT else "16:9"
            self._image_gen = GeminiImageGenerator(
                aspect_ratio=ar_value,
                reference_dir=self.resource_base / self.REFERENCES_DIR,
            )
        return self._image_gen

    @property
    def video_gen(self) -> GeminiVideoGenerator:
        if self._video_gen is None:
            ar_value = "9:16" if self.orientation == VideoOrientation.SHORT else "16:9"
            self._video_gen = GeminiVideoGenerator(
                aspect_ratio=ar_value,
                reference_dir=self.resource_base / self.REFERENCES_DIR,
            )
        return self._video_gen

    @property
    def audio_gen(self) -> GeminiAudioGenerator:
        if self._audio_gen is None:
            self._audio_gen = GeminiAudioGenerator(
                voice_name=self.prompt_manager.VOICE_NAME
            )
        return self._audio_gen

    @property
    def ffmpeg(self) -> FFmpegTool:
        if self._ffmpeg is None:
            self._ffmpeg = FFmpegTool()
        return self._ffmpeg

    @property
    def whisper(self) -> WhisperTool:
        if self._whisper is None:
            self._whisper = WhisperTool()
        return self._whisper

    @property
    def audio_tool(self) -> AudioTool:
        if self._audio_tool is None:
            bg_music_dir = self.resource_base / self.BG_MUSIC_DIR
            self._audio_tool = AudioTool(bg_music_dir=bg_music_dir)
        return self._audio_tool

    @property
    def google_drive(self) -> GoogleDriveTool:
        if self._google_drive is None:
            self._google_drive = GoogleDriveTool()
        return self._google_drive

    @property
    def youtube_uploader(self) -> YouTubeUploader:
        if self._youtube_uploader is None:
            self._youtube_uploader = YouTubeUploader()
        return self._youtube_uploader

    @property
    def prompt_manager(self) -> PromptManager:
        if self._prompt_manager is None:
            if self.orientation == VideoOrientation.SHORT:
                self._prompt_manager = PromptManagerShorts()
            elif self.orientation == VideoOrientation.LONG:
                self._prompt_manager = PromptManagerLongs()
            else:
                raise ValueError(f"Orientation {self.orientation} not supported.")
        return self._prompt_manager

    def load_json(
        self,
        idea_id: int,
        filename: str,
        model_class: Type[T],
    ) -> T:
        path = self.get_idea_path(idea_id) / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {filename} for project {idea_id}")
        return model_class.model_validate_json(path.read_text(encoding="utf-8"))

    def save_json(self, idea_id: int, filename: str, data: BaseModel):
        path = self.get_idea_path(idea_id) / filename
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def get_out_dir(self) -> Path:
        self.out_base.mkdir(parents=True, exist_ok=True)
        return self.out_base

    def get_ideas_dir(self) -> Path:
        path = self.out_base / self.IDEAS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def step1a_validate_quality(self, batch_size: int = 3):
        """
        Master Quality Validation: Evaluates scripts before production.
        """
        ideas = self.store.get_all_by_state(State.SCRIPT_GENERATED, limit=batch_size)
        if not ideas:
            return False

        Messenger.info(f"\n--- Validating quality for {len(ideas)} scripts ---")

        class ValidationResult(BaseModel):
            especificidad_puntos: int
            urgencia_puntos: int
            coherencia_puntos: int
            memorabilidad_puntos: int
            alineacion_puntos: int
            media: float
            decision: str
            mejoras_requeridas: str

        def validate_idea(idea_obj):
            try:
                script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)
                
                prompt = f"""Eres el editor jefe de "Eco del Colapso". Evalúa este Short.
TÍTULO: {idea_obj.title}
GANCHO: {script_data.scenes[0].narration}
CIERRE: {script_data.scenes[-1].narration}

Evalúa en escala 1-10:
1. ESPECIFICIDAD DEL GANCHO: (1 = abstracto / 10 = concreto)
2. URGENCIA EMOCIONAL: (1 = neutral / 10 = impactante)
3. COHERENCIA VISUAL: (1 = borroso / 10 = cinematográfico)
4. MEMORABILIDAD DEL CIERRE: (1 = genérico / 10 = único)
5. ALINEACIÓN CON MARCA: (1 = común / 10 = Eco del Colapso)

REGLA: Si la media < 7, RECHAZAR. 

Devuelve JSON:
{{
  "puntuaciones": {{...}},
  "media": 0.0,
  "decision": "APROBAR" o "RECHAZAR",
  "mejoras_requeridas": "instrucciones"
}}
"""
                result = self.text_gen.generate_text(prompt, ValidationResult)
                
                if result.decision == "APROBAR":
                    Messenger.success(f"ID {idea_obj.id} APROBADO (Score: {result.media})")
                    idea_obj.state = State.SCRIPT_VALIDATED
                else:
                    Messenger.warning(f"ID {idea_obj.id} RECHAZADO: {result.mejoras_requeridas}")
                    idea_obj.state = State.NEW # Reset to retry
                
                self.store.save(idea_obj)
                return True
            except Exception as e:
                Messenger.error(f"Error en validación ID {idea_obj.id}: {e}")
                return False

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(validate_idea, ideas))
        
        return any(results)

    def get_idea_path(self, idea_id: int) -> Path:
        folder_name = f"idea_{idea_id:06d}"
        path = self.get_ideas_dir() / folder_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_idea_subdir(self, idea_id: int, subdir: str) -> Path:
        path = self.get_idea_path(idea_id) / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_idea_asset_path(self, idea_id: int, subdir: str, filename: str) -> Path:
        return self.get_idea_subdir(idea_id, subdir) / filename

    def get_named_video_path(self, idea_id: int, title: str) -> Path:
        title_slug = slugify(title)
        return self.get_idea_path(idea_id) / f"{title_slug}.mp4"

    def step1_generate_story(self, batch_size: int = 3):
        Messenger.info("\n--- Generating cinematic concepts and scripts ---")
        
        # 1. Try to find existing NEW ideas
        ideas = self.store.get_all_by_state(State.NEW, limit=batch_size)
        if not ideas:
            return False

        def process_idea(idea_obj):
            try:
                Messenger.info(f"Processing existing NEW idea: {idea_obj.title}")
                from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea
                idea_data = self.load_json(idea_obj.id, self.IDEA_JSON, BaseIdea)
                
                script = self.prompt_manager.generate_script_from_idea(
                    self.text_gen, idea_data, idea_obj.category
                )
                self.save_json(idea_obj.id, self.SCRIPT_JSON, script)
                
                idea_obj.state = State.SCRIPT_GENERATED
                self.store.save(idea_obj)
                return True
            except Exception as e:
                Messenger.error(f"Failed to generate story for ID {idea_obj.id}: {e}")
                return False

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(process_idea, ideas))
        
        return any(results)

    def step2_generate_images(self, batch_size: int = 3):
        """
        Generate static images using Gemini for multiple ideas in parallel.
        """
        ideas = self.store.get_all_by_state(State.SCRIPT_VALIDATED, limit=batch_size)
        if not ideas:
            return False

        Messenger.info(f"\n--- Generating static images via Gemini for {len(ideas)} ideas ---")

        def process_idea_images(idea_obj):
            try:
                script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)
                tasks: List[ImageTask] = []
                for i, scene in enumerate(script_data.scenes):
                    out_path = self.get_idea_asset_path(
                        idea_obj.id, self.IMAGES_DIR, self.SCENE_IMAGE_PATTERN.format(i + 1)
                    )
                    if not out_path.exists():
                        tasks.append(
                            ImageTask(prompt=scene.image_prompt.formatted_prompt, output_path=out_path)
                        )

                if tasks:
                    self.image_gen.generate_images(tasks=tasks)

                missing_images = []
                for i, scene in enumerate(script_data.scenes):
                    out_path = self.get_idea_asset_path(
                        idea_obj.id, self.IMAGES_DIR, self.SCENE_IMAGE_PATTERN.format(i + 1)
                    )
                    if not out_path.exists():
                        missing_images.append(i + 1)
                
                if missing_images:
                    raise FileNotFoundError(f"Failed to generate images for scenes: {missing_images}")

                idea_obj.state = State.IMAGES_GENERATED
                self.store.save(idea_obj)
                return True
            except Exception as e:
                Messenger.error(f"Failed to generate images for ID {idea_obj.id}: {e}")
                return False

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(process_idea_images, ideas))
        
        return any(results)

    def step3_generate_videos(self, batch_size: int = 2):
        """
        Generate Native Videos via Veo 3.1 for multiple ideas in parallel.
        """
        ideas = self.store.get_all_by_state(State.IMAGES_GENERATED, limit=batch_size)
        if not ideas:
            return False

        Messenger.info(f"\n--- Generating native video clips via Veo 3.1 for {len(ideas)} ideas ---")

        def process_idea_videos(idea_obj):
            try:
                script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)

                class VideoTask(BaseModel):
                    prompt: str
                    output_path: Path
                    source_image: Optional[Path] = None

                tasks: List[VideoTask] = []
                for i, scene in enumerate(script_data.scenes):
                    out_path = self.get_idea_asset_path(
                        idea_obj.id, self.VIDEOS_DIR, self.SCENE_VIDEO_PATTERN.format(i + 1)
                    )
                    image_path = self.get_idea_asset_path(
                        idea_obj.id, self.IMAGES_DIR, self.SCENE_IMAGE_PATTERN.format(i + 1)
                    )
                    
                    if not out_path.exists():
                        tasks.append(
                            VideoTask(
                                prompt=scene.image_prompt.formatted_prompt, 
                                output_path=out_path,
                                source_image=image_path if image_path.exists() else None
                            )
                        )

                if tasks:
                    self.video_gen.generate_videos_batch(tasks=tasks)

                missing_videos = []
                for i, scene in enumerate(script_data.scenes):
                    out_path = self.get_idea_asset_path(
                        idea_obj.id, self.VIDEOS_DIR, self.SCENE_VIDEO_PATTERN.format(i + 1)
                    )
                    if not out_path.exists():
                        missing_videos.append(i + 1)
                
                if missing_videos:
                    raise FileNotFoundError(f"Failed to generate videos for scenes: {missing_videos}")

                idea_obj.state = State.VIDEOS_GENERATED
                self.store.save(idea_obj)
                return True
            except Exception as e:
                Messenger.error(f"Failed to generate videos for ID {idea_obj.id}: {e}")
                return False

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(process_idea_videos, ideas))
        
        return any(results)

    def step4_generate_audios(self):
        idea_obj = self.store.get_first_by_state(State.VIDEOS_GENERATED)
        if not idea_obj:
            return False

        Messenger.info("\n--- Generating batched audio for the script ---")
        script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)

        total_scenes = len(script_data.scenes)
        batch_size = 15

        for start_idx in range(0, total_scenes, batch_size):
            end_idx = min(start_idx + batch_size, total_scenes)
            chunk = script_data.scenes[start_idx:end_idx]
            batch_num = (start_idx // batch_size) + 1
            Messenger.info(f"Processing Batch {batch_num}: Scenes {start_idx + 1} to {end_idx}")

            missing_any = False
            for j in range(len(chunk)):
                scene_num = start_idx + j + 1
                out_path = self.get_idea_asset_path(
                    idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(scene_num)
                )
                if not out_path.exists():
                    missing_any = True
                    break

            if not missing_any:
                Messenger.info(f"Skipping Batch {batch_num}: All audio files exist.")
                continue

            chunk_filename = self.BATCH_AUDIO_PATTERN.format(batch_num)
            chunk_audio_path = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, chunk_filename)
            Messenger.info(f"Synthesizing audio for Batch {batch_num}...")
            chunk_text = "\n\n".join([s.narration for s in chunk])
            # Format audio for better pacing
            full_narration = " ".join([s.narration for s in chunk])
            formatted_audio_prompt = self.prompt_manager.get_audio_prompt(full_narration)
            
            class FormattedAudio(BaseModel):
                texto_formateado: str
                velocidad_recomendada: float
                voz_recomendada: str

            formatted_result = self.text_gen.generate_text(formatted_audio_prompt, FormattedAudio)
            
            # Clean tags for TTS if necessary (some TTS don't like [tags])
            # For Gemini TTS, we'll replace [pausa_corta] with ", " and [pausa_larga] with "... "
            clean_text = formatted_result.texto_formateado.replace("[pausa_corta]", ", ").replace("[pausa_larga]", "... ").replace("[énfasis]", "")
            
            self.audio_gen.text_to_speech(clean_text, chunk_audio_path)

            Messenger.info(f"Transcribing Batch {batch_num} for alignment...")
            segments = self.whisper.get_transcription_segments(chunk_audio_path)

            Messenger.info(f"Aligning Batch {batch_num} via Gemini...")
            chunk_script_texts = [s.narration for s in chunk]
            prompt = self.prompt_manager.get_alignment_prompt(segments, chunk_script_texts)
            alignment = self.text_gen.generate_text(prompt, AudioAlignment)

            if len(alignment.alignments) != len(chunk):
                chunk_audio_path.unlink(missing_ok=True)
                chunk_audio_path.with_name(chunk_audio_path.name + ".json").unlink(missing_ok=True)
                raise RuntimeError(f"Alignment mismatch in Batch {batch_num}: Expected {len(chunk)}, got {len(alignment.alignments)}")

            Messenger.info(f"Splitting Batch {batch_num} into {len(chunk)} scene audios...")
            for al in alignment.alignments:
                absolute_scene_num = start_idx + al.scene_number
                out_path = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(absolute_scene_num))
                duration = al.end_time - al.start_time
                if duration < 0.5:
                    chunk_audio_path.unlink(missing_ok=True)
                    chunk_audio_path.with_name(chunk_audio_path.name + ".json").unlink(missing_ok=True)
                    raise RuntimeError(f"Invalid duration (Scene {absolute_scene_num}): {duration:.3f}s. Forcing retry.")

                self.ffmpeg.split_audio(audio_in=chunk_audio_path, audio_out=out_path, start_time=al.start_time, duration=duration)

            chunk_audio_path.unlink(missing_ok=True)

        idea_obj.state = State.AUDIO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 4 ready: {State.AUDIO_GENERATED} finalized.\n")
        return True

    def step5_sync_videos(self):
        """
        Sync Videos: Stretches/Shrinks AI-generated videos to match narration duration.
        """
        idea_obj = self.store.get_first_by_state(State.AUDIO_GENERATED)
        if not idea_obj:
            return False

        Messenger.info("\n--- Syncing native videos with narration ---")
        script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)

        scene_videos: List[Path] = []
        for i in range(len(script_data.scenes)):
            raw_ai_video = self.get_idea_asset_path(idea_obj.id, self.VIDEOS_DIR, self.SCENE_VIDEO_PATTERN.format(i + 1))
            audio_path = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(i + 1))
            
            if not raw_ai_video.exists():
                Messenger.error(f"Missing video for Scene {i+1}. Rolling back to IMAGES_GENERATED.")
                idea_obj.state = State.IMAGES_GENERATED
                self.store.save(idea_obj)
                return False
            
            if not audio_path.exists():
                Messenger.error(f"Missing audio for Scene {i+1}. Rolling back to VIDEOS_GENERATED.")
                idea_obj.state = State.VIDEOS_GENERATED
                self.store.save(idea_obj)
                return False

            # Temporary sync file
            synced_video = raw_ai_video.with_name(f"synced_{raw_ai_video.name}")
            
            Messenger.info(f"Syncing Scene {i+1}...")
            self.ffmpeg.sync_video_and_audio(raw_ai_video, audio_path, synced_video)
            scene_videos.append(synced_video)

        # Final video concatenation.
        raw_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        self.ffmpeg.concat_videos(scene_videos, raw_video)

        # Cleanup synced parts
        for v in scene_videos:
            try:
                v.unlink(missing_ok=True)
            except Exception:
                pass

        idea_obj.state = State.VIDEO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 5 ready: {State.VIDEO_GENERATED} finalized.\n")
        return True

    def step6_generate_subtitles(self):
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED)
        if not idea_obj:
            return False

        Messenger.info("\n--- Generating subtitles for the video ---")
        raw_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.RAW_VIDEO)
        audio_wav = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_AUDIO)
        subs_srt = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_SUBS)
        subtitled_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.SUBTITLED_VIDEO)

        self.ffmpeg.extract_audio(raw_video, audio_wav)
        self.whisper.generate_srt(audio_wav, subs_srt)
        self.ffmpeg.add_subtitles_to_video(raw_video, subs_srt, subtitled_video)

        idea_obj.state = State.VIDEO_SUBTITLED
        self.store.save(idea_obj)
        Messenger.success(f"Step 6 ready: {State.VIDEO_SUBTITLED} finalized.\n")
        return True

    def step7_add_background_music(self):
        idea_obj = self.store.get_first_by_state(State.VIDEO_SUBTITLED)
        if not idea_obj:
            return False

        Messenger.info("\n--- Adding background music ---")
        subtitled_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.SUBTITLED_VIDEO)
        final_with_music = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO)

        selected_music = self.audio_tool.get_random_audio()
        if not selected_music:
            return

        self.ffmpeg.add_background_music(subtitled_video, selected_music, final_with_music, bg_volume=0.18)

        idea_obj.state = State.VIDEO_MUSIC_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 7 ready: {State.VIDEO_MUSIC_GENERATED} finalized.\n")
        return True

    def step8_generate_metadata(self):
        idea_obj = self.store.get_first_by_state(State.VIDEO_MUSIC_GENERATED)
        if not idea_obj:
            return False

        Messenger.info("\n--- Generating SEO Metadata ---")
        script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)
        
        full_narration = "\n".join([s.narration for s in script_data.scenes])
        prompt = SeoPromptManager.get_seo_prompt(idea_obj.title, full_narration)
        
        # We can just define an ad-hoc schema here or use plain text.
        # Let's generate it as a JSON block using the text generator with a mock structure.
        from pydantic import BaseModel
        class SeoData(BaseModel):
            youtube_title: str
            youtube_description: str
            tiktok_caption: str
            instagram_caption: str
            facebook_caption: str
            
        seo_data = self.text_gen.generate_text(prompt, SeoData)
        
        # Save JSON (original state)
        self.save_json(idea_obj.id, self.SEO_METADATA_JSON, seo_data)

        # Save readable TXT with matching name
        video_title_slug = slugify(idea_obj.title if idea_obj.title else f"video_{idea_obj.id}")
        seo_txt_path = self.get_idea_path(idea_obj.id) / f"{video_title_slug}_SEO.txt"
        
        try:
            with open(seo_txt_path, "w", encoding="utf-8") as f:
                f.write(f"TITULO YOUTUBE: {seo_data.youtube_title}\n\n")
                f.write(f"DESCRIPCION YOUTUBE:\n{seo_data.youtube_description}\n\n")
                f.write(f"--- REDES SOCIALES ---\n\n")
                f.write(f"TIKTOK:\n{seo_data.tiktok_caption}\n\n")
                f.write(f"INSTAGRAM:\n{seo_data.instagram_caption}\n\n")
                f.write(f"FACEBOOK:\n{seo_data.facebook_caption}\n")
        except Exception as e:
            Messenger.warning(f"Could not write SEO TXT file: {e}. Proceeding with JSON only.")

        idea_obj.state = State.METADATA_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 8 ready: {State.METADATA_GENERATED} finalized.\n")
        return True

    def step9_upload_to_drive(self):
        idea_obj = self.store.get_first_by_state(State.METADATA_GENERATED)
        if not idea_obj:
            return False

        # Persistent check: if ID already exists, just move state
        if idea_obj.drive_file_id:
            Messenger.success(f"Video already on Drive (ID: {idea_obj.drive_file_id}). skipping upload.")
            idea_obj.state = State.UPLOADED_TO_DRIVE
            self.store.save(idea_obj)
            return True

        Messenger.info("\n--- Uploading to Google Drive ---")
        final_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO)
        
        idea_path = self.get_idea_path(idea_obj.id)
        seo_files = list(idea_path.glob("*_SEO.txt"))
        if not seo_files:
            Messenger.error(f"No SEO file found for ID {idea_obj.id}")
            return False
        
        seo_file = seo_files[0]
        video_title_slug = slugify(idea_obj.title if idea_obj.title else f"video_{idea_obj.id}")
        
        drive_video_name = f"{video_title_slug}.mp4"
        drive_seo_name = seo_file.name

        import os
        folder_id = os.getenv("DRIVE_FOLDER_ID")

        try:
            video_id = self.google_drive.upload_file(final_video, "video/mp4", folder_id, display_name=drive_video_name)
            # Store the ID persistently
            idea_obj.drive_file_id = video_id
            
            seo_id = self.google_drive.upload_file(seo_file, "text/plain", folder_id, display_name=drive_seo_name)
            
            Messenger.success(f"Uploaded Video ID: {video_id} | SEO ID: {seo_id}")
            
            idea_obj.state = State.UPLOADED_TO_DRIVE
            self.store.save(idea_obj)
            Messenger.success(f"Step 9 ready: {State.UPLOADED_TO_DRIVE} finalized.\n")
            return True
        except Exception as e:
            Messenger.error(f"Failed to upload to Google Drive: {e}")
            return False

    def step10_publish_to_youtube(self):
        """
        Uploads and schedules the video to YouTube Shorts.
        """
        idea_obj = self.store.get_first_by_state(State.UPLOADED_TO_DRIVE)
        if not idea_obj:
            return False

        Messenger.info(f"\n--- Publishing to YouTube: {idea_obj.title} ---")
        
        # Load SEO metadata
        seo_path = self.get_idea_asset_path(idea_obj.id, "", self.SEO_METADATA_JSON)
        from pydantic import BaseModel
        class SeoData(BaseModel):
            youtube_title: str
            youtube_description: str
            tiktok_caption: str
            instagram_caption: str
            facebook_caption: str

        if not seo_path.exists():
            Messenger.warning(f"Metadata missing for ID {idea_obj.id}. Re-generating...")
            # If we don't have the script, we generate SEO from title only
            script_path = self.get_idea_asset_path(idea_obj.id, "", self.SCRIPT_JSON)
            full_narration = ""
            if script_path.exists():
                from flows.image_content_generator.pipeline.prompt_shorts.manager import VideoScript
                script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)
                full_narration = "\n".join([s.narration for s in script_data.scenes])
            
            from tools.text_generation.seo_prompts import SeoPromptManager
            prompt = SeoPromptManager.get_seo_prompt(idea_obj.title, full_narration)
            seo_data = self.text_gen.generate_text(prompt, SeoData)
            self.save_json(idea_obj.id, self.SEO_METADATA_JSON, seo_data)
        else:
            seo_data = self.load_json(idea_obj.id, self.SEO_METADATA_JSON, SeoData)
        
        final_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO)

        if idea_obj.youtube_video_id:
            Messenger.success(f"Video already published to YouTube (ID: {idea_obj.youtube_video_id}). skipping.")
            idea_obj.state = State.PUBLISHED_TO_YOUTUBE
            self.store.save(idea_obj)
            return True

        # Get next available slot (10 AM)
        next_slot = YouTubeScheduler.get_next_slot()
        
        try:
            yt_id = self.youtube_uploader.upload_video(
                file_path=str(final_video),
                title=seo_data.youtube_title,
                description=seo_data.youtube_description,
                tags=["Shorts", "EcoDelColapso", "Anime90s", "Distopia"],
                publish_at=next_slot
            )
            
            idea_obj.youtube_video_id = yt_id
            idea_obj.state = State.PUBLISHED_TO_YOUTUBE
            self.store.save(idea_obj)
            Messenger.success(f"Step 10 ready: Scheduled for {next_slot}")
            return True
        except Exception as e:
            Messenger.error(f"Failed to publish to YouTube: {e}")
            return False

    def step11_rename_final_video(self):
        idea_obj = self.store.get_first_by_state(State.PUBLISHED_TO_YOUTUBE)
        if not idea_obj:
            return False

        Messenger.info("\n--- Final Renaming ---")
        final_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO)
        video_title = idea_obj.title if idea_obj.title else f"video_{idea_obj.id}"
        named_final = self.get_named_video_path(idea_obj.id, video_title)
        
        if final_video.exists():
            final_video.rename(named_final)
            
        idea_obj.state = State.COMPLETED
        self.store.save(idea_obj)
        Messenger.success(f"Step 11 ready: {State.COMPLETED} finalized.\n")
        return True

    def step12_cleanup_completed(self):
        """
        Deletes the local folder for completed ideas to save disk space.
        Only runs if state is COMPLETED (verified Drive + YouTube).
        """
        idea_obj = self.store.get_first_by_state(State.COMPLETED)
        if not idea_obj:
            return False

        Messenger.info(f"\n--- Cleaning up local files for ID {idea_obj.id}: {idea_obj.title} ---")
        idea_path = self.get_idea_path(idea_obj.id)
        
        if idea_path.exists():
            import shutil
            try:
                shutil.rmtree(idea_path)
                Messenger.success(f"Deleted local folder: {idea_path}")
            except Exception as e:
                Messenger.error(f"Failed to delete local folder: {e}")
                return False

        idea_obj.state = State.ARCHIVED
        self.store.save(idea_obj)
        Messenger.success(f"Step 12 ready: Idea {idea_obj.id} moved to {State.ARCHIVED}\n")
        return True
