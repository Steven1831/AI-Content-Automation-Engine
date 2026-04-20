import random
from typing import Sequence, Type

from pydantic import BaseModel

from flows.image_content_generator.pipeline.prompt_base import constants
from flows.image_content_generator.pipeline.prompt_base.models import (
    CategoryHandler,
    SelectedConfig,
)
from tools.video_editing.whisper_schemas import WhisperTranscriptionSegment


class BasePromptManager(BaseModel):
    """
    Base manager for prompts
    """

    # Prompts
    IMAGE_PROMPT: str = constants.IMAGE_PROMPT
    AUDIO_PROMPT: str = constants.AUDIO_PROMPT
    ALIGNMENT_PROMPT: str = constants.ALIGNMENT_PROMPT

    # Voice
    VOICE_NAME: str = "Fenrir"

    CATEGORIES: Sequence[Type[CategoryHandler]] = []

    def select_random_config(self) -> SelectedConfig:
        """Picks a random handler and idea variant, returning a unified configuration object."""
        selected_category = random.choice(self.CATEGORIES)
        idea_model = selected_category.get_random_idea_variant()

        return SelectedConfig(
            category=f"{selected_category.__name__}_{idea_model.__name__}",
            handler=selected_category,
            idea_prompt=idea_model.get_idea_prompt(),
            idea_model=idea_model,
        )

    def get_audio_prompt(self, audio_text: str) -> str:
        """Formats the audio prompt."""
        return self.AUDIO_PROMPT.format(audio_text=audio_text)

    def get_alignment_prompt(
        self,
        whisper_segments: Sequence[WhisperTranscriptionSegment],
        script_scenes: Sequence[str],
    ) -> str:
        """Formats the alignment prompt."""
        whisper_data = "\n".join([
            f"[{s.start:.3f}s-{s.end:.3f}s] {s.text}"
            for s in whisper_segments
        ])
        scenes_data = "\n".join([
            f"Escena {i+1}: {text}"
            for i, text in enumerate(script_scenes)
        ])
        return self.ALIGNMENT_PROMPT.format(
            whisper_data=whisper_data,
            scenes_data=scenes_data,
            expected_count=len(script_scenes)
        )
