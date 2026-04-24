import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation
from tools.common.messenger import Messenger

RESOURCE_BASE = Path("flows/image_content_generator/resource")
SHORT_OUT_BASE = Path("flows/image_content_generator/out_short")

def start_production(count: int = 6):
    pipeline = Pipeline(
        out_base=SHORT_OUT_BASE,
        resource_base=RESOURCE_BASE,
        orientation=VideoOrientation.SHORT
    )

    Messenger.info(f"--- Starting Veo 3.1 Production for {count} Shorts ---")

    for i in range(count):
        Messenger.info(f"--- PRODUCING SHORT #{i+1} OF {count} ---")
        
        # Step 1: Script
        pipeline.step1_generate_story()
        
        # Step 2: Native Video Generation (Veo 3.1)
        pipeline.step2_generate_videos()
        
        # Step 3: Audio (Gemini TTS)
        pipeline.step3_generate_audios()
        
        # Step 4: Sync Video with Audio
        pipeline.step4_sync_videos()
        
        # Step 5: Subtitles
        pipeline.step5_generate_subtitles()
        
        # Step 6: Background Music
        pipeline.step6_add_background_music()
        
        # Step 7: Final Rename
        pipeline.step7_rename_final_video()

    Messenger.success(f"--- Production Complete: {count} videos generated with Veo 3.1 ---")

if __name__ == "__main__":
    start_production(6)
