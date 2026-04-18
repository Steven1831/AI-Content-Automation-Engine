# Standard: main.py

The `main.py` file is the primary entry point for a project's pipeline.

## Requirements
- **CLI Argument Parsing:** Use `argparse` to allow selecting specific steps or `all`.
- **Strict Path Usage:** Use `pathlib.Path` for all base directories (e.g., `OUT_BASE`, `RESOURCE_BASE`).
- **Consolidated Resources:** Group all static assets (bg-music, style-refs) under a single `RESOURCE_BASE` path.
- **Initialization:** Initialize the `Pipeline` class with `out_base` and `resource_base` Path objects.
- **Infinite Loop:** Supporting continuous automation via a `while True` loop for the `all` step.

## Example Structure
```python
from enum import Enum
from pathlib import Path
from tools.common.messenger import Messenger

class PipelineStep(str, Enum):
    ALL = "all"
    STEP1 = "step1"
    STEP2 = "step2"
    ...

OUT_BASE = Path("flows/project/out")
RESOURCE_BASE = Path("flows/project/resource")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=PipelineStep, choices=list(PipelineStep))
    args = parser.parse_args()

    pipeline = VideoPipeline(out_base=OUT_BASE, resource_base=RESOURCE_BASE)

    # Map Enum members to their corresponding pipeline methods
    step_methods = {
        PipelineStep.STEP1: pipeline.step1_method,
        PipelineStep.STEP2: pipeline.step2_method,
        ...
    }

    # Define steps to execute (excluding 'all' itself)
    steps = [s for s in PipelineStep if s != PipelineStep.ALL]

    if args.step == PipelineStep.ALL:
        while True:
            Messenger.info("--- Starting New Cycle ---")
            for step in steps:
                step_methods[step]()
            Messenger.success("Cycle completed.")
    else:
        # Run specific step
        step_methods[args.step]()
```
