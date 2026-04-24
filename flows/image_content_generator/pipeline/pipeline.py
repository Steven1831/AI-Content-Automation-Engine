from pathlib import Path
from typing import Any, ClassVar, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, PrivateAttr

from flows.image_content_generator.pipeline.prompt_base.models import VideoScript
from flows.image_content_generator.pipeline.prompt_longs.manager import PromptManagerLongs
from flows.image_content_generator.pipeline.prompt_shorts.manager import PromptManagerShorts
from flows.image_content_generator.pipeline.schemas import AudioAlignment, State, VideoOrientation
from flows.image_content_generator.pipeline.storage_csv import CsvStore
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
    _store: Optional[CsvStore] = PrivateAttr(default=None)

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

    # Standard Scene Patterns
    SCENE_IMAGE_PATTERN: ClassVar[str] = "scene_{}.png"
    SCENE_AUDIO_PATTERN: ClassVar[str] = "scene_{}.wav"
    SCENE_VIDEO_PATTERN: ClassVar[str] = "scene_{}.mp4"
    BATCH_AUDIO_PATTERN: ClassVar[str] = "batch_{}.wav"

    # Standard Resource Directories
    BG_MUSIC_DIR: ClassVar[str] = "bg-music"
    REFERENCES_DIR: ClassVar[str] = "reference"

    # Standard Tracking Files
    IDEAS_TRACKING_CSV: ClassVar[str] = "ideas_tracking.csv"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def store(self) -> CsvStore:
        if self._store is None:
            csv_path = self.out_base / self.IDEAS_TRACKING_CSV
            self._store = CsvStore(csv_path=csv_path)
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
        path = self.get_out_dir() / self.IDEAS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

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

    def step1_generate_story(self):
        Messenger.info("\n--- Generating cinematic concept and script ---")
        idea_data, script, category = self.prompt_manager.generate_full_story(self.text_gen)
        idea_obj = self.store.add_new_idea(idea_data.title, category)
        self.save_json(idea_obj.id, self.IDEA_JSON, idea_data)
        self.save_json(idea_obj.id, self.SCRIPT_JSON, script)
        idea_obj.state = State.SCRIPT_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 1 ready: {State.SCRIPT_GENERATED} finalized.\n")

    def step2_generate_videos(self):
        """
        Generate Native Videos via Veo 3.1.
        """
        idea_obj = self.store.get_first_by_state(State.SCRIPT_GENERATED)
        if not idea_obj:
            Messenger.error("No script ready for video generation.")
            return

        Messenger.info("\n--- Generating native video clips via Veo 3.1 ---")
        script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)

        class VideoTask(BaseModel):
            prompt: str
            output_path: Path

        tasks: List[VideoTask] = []
        for i, scene in enumerate(script_data.scenes):
            out_path = self.get_idea_asset_path(
                idea_obj.id, self.VIDEOS_DIR, self.SCENE_VIDEO_PATTERN.format(i + 1)
            )
            if out_path.exists():
                Messenger.info(f"Skipping Scene {i+1} video: File already exists.")
                continue

            tasks.append(
                VideoTask(prompt=scene.image_prompt.formatted_prompt, output_path=out_path)
            )

        # Process video generation (native movement!)
        self.video_gen.generate_videos_batch(tasks=tasks)

        idea_obj.state = State.VIDEOS_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 2 ready: {State.VIDEOS_GENERATED} finalized.\n")

    @retry(max_attempts=3)
    def step3_generate_audios(self):
        idea_obj = self.store.get_first_by_state(State.VIDEOS_GENERATED)
        if not idea_obj:
            Messenger.error("No videos ready for audio generation.")
            return

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
            formatted_audio = self.prompt_manager.get_audio_prompt(chunk_text)
            self.audio_gen.text_to_speech(formatted_audio, chunk_audio_path)

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
        Messenger.success(f"Step 3 ready: {State.AUDIO_GENERATED} finalized.\n")

    def step4_sync_videos(self):
        """
        Sync Videos: Stretches/Shrinks AI-generated videos to match narration duration.
        """
        idea_obj = self.store.get_first_by_state(State.AUDIO_GENERATED)
        if not idea_obj:
            Messenger.error("No audio ready for video sync.")
            return

        Messenger.info("\n--- Syncing native videos with narration ---")
        script_data = self.load_json(idea_obj.id, self.SCRIPT_JSON, VideoScript)

        scene_videos: List[Path] = []
        for i in range(len(script_data.scenes)):
            raw_ai_video = self.get_idea_asset_path(idea_obj.id, self.VIDEOS_DIR, self.SCENE_VIDEO_PATTERN.format(i + 1))
            audio_path = self.get_idea_asset_path(idea_obj.id, self.AUDIOS_DIR, self.SCENE_AUDIO_PATTERN.format(i + 1))
            
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
            v.unlink(missing_ok=True)

        idea_obj.state = State.VIDEO_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 4 ready: {State.VIDEO_GENERATED} finalized.\n")

    def step5_generate_subtitles(self):
        idea_obj = self.store.get_first_by_state(State.VIDEO_GENERATED)
        if not idea_obj:
            Messenger.error("No video ready for subtitle generation.")
            return

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
        Messenger.success(f"Step 5 ready: {State.VIDEO_SUBTITLED} finalized.\n")

    def step6_add_background_music(self):
        idea_obj = self.store.get_first_by_state(State.VIDEO_SUBTITLED)
        if not idea_obj:
            Messenger.error("No subtitled video found to add music.")
            return

        Messenger.info("\n--- Adding background music ---")
        subtitled_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.SUBTITLED_VIDEO)
        final_with_music = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO)

        selected_music = self.audio_tool.get_random_audio()
        if not selected_music:
            return

        self.ffmpeg.add_background_music(subtitled_video, selected_music, final_with_music, bg_volume=0.18)

        idea_obj.state = State.VIDEO_MUSIC_GENERATED
        self.store.save(idea_obj)
        Messenger.success(f"Step 6 ready: {State.VIDEO_MUSIC_GENERATED} finalized.\n")

    def step7_rename_final_video(self):
        idea_obj = self.store.get_first_by_state(State.VIDEO_MUSIC_GENERATED)
        if not idea_obj:
            Messenger.error("No video with music found to rename.")
            return

        Messenger.info("\n--- Final Renaming ---")
        final_video = self.get_idea_asset_path(idea_obj.id, self.EDITIONS_DIR, self.FINAL_VIDEO)
        video_title = idea_obj.title if idea_obj.title else f"video_{idea_obj.id}"
        named_final = self.get_named_video_path(idea_obj.id, video_title)
        final_video.rename(named_final)

        idea_obj.state = State.COMPLETED
        self.store.save(idea_obj)
        Messenger.success(f"Step 7 ready: {State.COMPLETED} finalized.\n")
