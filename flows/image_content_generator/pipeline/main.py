import argparse
from enum import Enum
from pathlib import Path

from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation
from tools.common.messenger import Messenger

RESOURCE_BASE = Path("flows/image_content_generator/resource")
LONG_OUT_BASE = Path("flows/image_content_generator/out_long")
SHORT_OUT_BASE = Path("flows/image_content_generator/out_short")


class PipelineStep(str, Enum):
    ALL = "all"
    STEP1 = "step1"
    STEP2 = "step2"
    STEP3 = "step3"
    STEP4 = "step4"
    STEP5 = "step5"
    STEP6 = "step6"
    STEP7 = "step7"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orientation", type=VideoOrientation, choices=list(VideoOrientation))
    parser.add_argument("step", type=PipelineStep, choices=list(PipelineStep))
    args = parser.parse_args()

    # Determine output base based on orientation
    out_base = SHORT_OUT_BASE if args.orientation == VideoOrientation.SHORT else LONG_OUT_BASE

    pipeline = Pipeline(
        out_base=out_base,
        resource_base=RESOURCE_BASE,
        orientation=args.orientation
    )

    # Map Enum members to their corresponding pipeline methods
    step_methods = {
        PipelineStep.STEP1: pipeline.step1_generate_story,
        PipelineStep.STEP2: pipeline.step2_generate_images,
        PipelineStep.STEP3: pipeline.step3_generate_audios,
        PipelineStep.STEP4: pipeline.step4_generate_videos,
        PipelineStep.STEP5: pipeline.step5_generate_subtitles,
        PipelineStep.STEP6: pipeline.step6_add_background_music,
        PipelineStep.STEP7: pipeline.step7_rename_final_video,
    }

    # Define steps to execute (excluding 'all' itself)
    steps = [s for s in PipelineStep if s != PipelineStep.ALL]

    if args.step == PipelineStep.ALL:
        Messenger.info("--- Starting Infinite Generation Loop ---")
        while True:
            for step in steps:
                step_methods[step]()
            Messenger.success("Cycle completed. Starting next cycle...")
    else:
        # Run specific step
        step_methods[args.step]()


if __name__ == "__main__":
    main()
