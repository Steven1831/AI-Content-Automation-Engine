import time
from pathlib import Path
from typing import Any, List, Optional

from google.genai import types
from PIL import Image

from tools.common.gemini_base import GeminiBase
from tools.common.messenger import Messenger


class GeminiVideoGenerator(GeminiBase):
    """
    Tool for generating video clips using Google Veo 3.1.
    """
    video_model: str = "veo-3.1-generate-preview"
    aspect_ratio: str
    style_references: List[Path] = []

    def __init__(
        self,
        aspect_ratio: str,
        reference_dir: Optional[Path] = None,
        **kwargs: Any
    ) -> None:
        style_refs = []
        if reference_dir and reference_dir.exists():
            style_refs = sorted(reference_dir.glob("*.png"))

        super().__init__(
            aspect_ratio=aspect_ratio,
            style_references=style_refs,
            **kwargs
        )

    def generate_video(
        self,
        prompt: str,
        output_path: Path,
        style_references: List[Path] = []
    ) -> None:
        """
        Generates a video clip using Veo 3.1 and saves it to disk.
        This is an asynchronous operation that polls for completion.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        Messenger.info(f"Starting Veo 3.1 video generation for: {output_path.name}")
        
        # Guide the generation with style references if provided
        # Veo supports up to 3 reference images in the config
        config = types.GenerateVideosConfig(
            aspect_ratio=self.aspect_ratio,
        )
        
        # Start the video generation operation
        operation = self.client.models.generate_videos(
            model=self.video_model,
            prompt=prompt,
            config=config
        )

        # Poll for completion
        start_time = time.time()
        max_wait = 600 # 10 minutes timeout
        
        while not operation.done:
            elapsed = int(time.time() - start_time)
            if elapsed > max_wait:
                raise RuntimeError(f"Video generation timed out after {max_wait}s")
            
            Messenger.info(f"Veo 3.1: Generation in progress... ({elapsed}s)")
            time.sleep(20)
            operation.refresh()

        if operation.result:
            video = operation.result
            # Write video data to file
            for part in video.generated_video:
                 with open(output_path, "wb") as f:
                     f.write(part.video.data)
            
            Messenger.success(f"Video generated successfully: {output_path}")
        else:
            raise RuntimeError("Veo 3.1 failed to return a result.")

    def generate_videos_batch(self, tasks: List[Any]) -> None:
        """
        Processes a list of video generation tasks sequentially.
        """
        total = len(tasks)
        Messenger.info(f"Batch Processing: {total} video clips via Veo 3.1")

        for i, task in enumerate(tasks, start=1):
            Messenger.info(f"Processing Clip {i}/{total}: {task.output_path.name}")
            try:
                self.generate_video(
                    prompt=task.prompt,
                    output_path=task.output_path,
                    style_references=self.style_references
                )
            except Exception as e:
                Messenger.error(f"Failed to generate clip {i}: {str(e)}")
                # Continue with next clips instead of crashing whole batch
                continue

        Messenger.step_success(f"Batch complete: {total} video clips processed.")
