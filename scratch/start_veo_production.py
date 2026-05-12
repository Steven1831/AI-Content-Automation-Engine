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

    Messenger.info("--- Starting Persistent Production Loop ---")
    import time

    while True:
        progress_made = False
        
        try:
            # 1. Prioritize Finishing and Cleaning (Steps 12 down to 4)
            if pipeline.step12_cleanup_completed(): progress_made = True
            if pipeline.step11_rename_final_video(): progress_made = True
            if pipeline.step10_publish_to_youtube(): progress_made = True
            if pipeline.step9_upload_to_drive(): progress_made = True
            if pipeline.step8_generate_metadata(): progress_made = True
            if pipeline.step7_add_background_music(): progress_made = True
            if pipeline.step6_generate_subtitles(): progress_made = True
            if pipeline.step5_sync_videos(): progress_made = True
            if pipeline.step4_generate_audios(): progress_made = True
            
            # 2. Parallel Processing for heavy steps (3, 2, 1, 1a)
            if pipeline.step3_generate_videos(batch_size=2): progress_made = True
            if pipeline.step2_generate_images(batch_size=3): progress_made = True
            if pipeline.step1a_validate_quality(batch_size=5): progress_made = True
            if pipeline.step1_generate_story(batch_size=5): progress_made = True
        except Exception as e:
            Messenger.error(f"Critical error in production loop: {e}")
            time.sleep(30)
            continue
        
        if not progress_made:
            Messenger.info("Queue empty or stuck. Waiting 60 seconds before next check...")
            time.sleep(60)

    Messenger.success(f"--- Production Complete: {count} videos generated with Veo 3.1 ---")

if __name__ == "__main__":
    start_production(6)
