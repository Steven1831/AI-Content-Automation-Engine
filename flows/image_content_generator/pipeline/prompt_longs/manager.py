from typing import List, Sequence, Tuple, Type

from flows.image_content_generator.pipeline.prompt_base.manager import BasePromptManager
from flows.image_content_generator.pipeline.prompt_base.models import (
    BaseIdea,
    CategoryHandler,
    Scene,
    VideoScript,
)
from flows.image_content_generator.pipeline.prompt_longs.finances.models import FinancesHandlerLong
from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator


class PromptManagerLongs(BasePromptManager):
    """Manager specific to Long videos (16:9), aggregating modular categories."""

    CATEGORIES: Sequence[Type[CategoryHandler]] = [
        FinancesHandlerLong,
    ]

    def generate_full_story(
        self, text_gen: GeminiTextGenerator
    ) -> Tuple[BaseIdea, VideoScript, str]:
        """
        Executes the generation loop in 3 steps:
        1. Random Selection: Pick a category config.
        2. Idea Generation: Prompt for initial idea.
        3. Script Generation: Build multi-chunk script from idea.
        """
        # 1. Random Selection
        config = self.select_random_config()

        # 2. Idea Generation
        idea_data = text_gen.generate_text(config.idea_prompt, config.idea_model)

        # 3. Script Generation
        Messenger.info(f"\n--- Generating script for: {idea_data.title} ---")
        all_scenes: List[Scene] = []
        num_chunks = 6
        scenes_per_chunk = 20
        base_prompt = config.handler.get_full_script_prompt(idea_data)

        for i in range(num_chunks):
            start_scene = (i * scenes_per_chunk) + 1
            end_scene = start_scene + scenes_per_chunk - 1

            Messenger.info(
                f"Generating chunk {i+1}/{num_chunks} (Scenes {start_scene}-{end_scene})..."
            )

            context = "Inicio de la historia."
            if all_scenes:
                # Get last 3 scenes for context
                last_scenes = all_scenes[-3:]
                context = "Resumen de las últimas escenas para continuidad:\n"
                for s in last_scenes:
                    context += f"- Escena {s.scene_number}\n"

            prompt = config.handler.get_chunked_script_prompt(
                base_prompt=base_prompt,
                start_scene=start_scene,
                end_scene=end_scene,
                context=context,
            )

            chunk_script = text_gen.generate_text(prompt, VideoScript)
            all_scenes.extend(chunk_script.scenes)

        script = VideoScript(scenes=all_scenes)
        return idea_data, script, config.category
