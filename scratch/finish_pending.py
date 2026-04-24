from pathlib import Path
from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation, State
from tools.common.messenger import Messenger

SHORT_OUT_BASE = Path("flows/image_content_generator/out_short")
RESOURCE_BASE = Path("flows/image_content_generator/resource")

def finish_pending():
    pipeline = Pipeline(
        out_base=SHORT_OUT_BASE,
        resource_base=RESOURCE_BASE,
        orientation=VideoOrientation.SHORT
    )
    
    steps = [
        pipeline.step2_generate_images,
        pipeline.step3_generate_audios,
        pipeline.step4_generate_videos,
        pipeline.step5_generate_subtitles,
        pipeline.step6_add_background_music,
        pipeline.step7_rename_final_video,
    ]
    
    Messenger.info("--- Finishing Pending Ideas (1 to 6) ---")
    
    while True:
        # Check if there are any ideas not COMPLETED
        pending = [i for i in pipeline.store.load_all() if i.state != State.COMPLETED]
        if not pending:
            Messenger.success("All ideas completed!")
            break
            
        for step in steps:
            step()

if __name__ == "__main__":
    finish_pending()
