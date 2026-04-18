# 01. Architecture Patterns

Standardized structural guidelines for the video automation repository.

## 1. Repository Layout
- `flows/`: Concrete implementations of pipelines (products).
- `tools/`: Shared, reusable logic components (infrastructure).
- `.rules/`: Documentation of standards and agent guidelines.

## 2. Flow Structure
Every flow under `flows/` must follow:
- `pipeline/`: Core logic (entry points, pipeline class, schemas).
- `out/`: Data persistence and generated assets.
- `resource/`: Templates and static assets.

## 3. File-Level Standards
Every `pipeline/` directory must contain the following standardized files:

- [**`main.py`**](standards/main.md): CLI Entry point, step selection, and infinite loops.
- [**`pipeline.py`**](standards/pipeline.md): Process orchestration and lazy loading.
- [**`constants.py`**](standards/constants.md): Static project configuration.
- [**`prompt_*/` (Directories)**](standards/prompts.md): Modular prompt generation architecture (models, manager, constants).
- [**`schemas.py`**](standards/schemas.md): Pure Pydantic data structures, domain models, and lifecycle Enums.
- [**`storage_csv.py`**](standards/storage_csv.md): Persistence using `CsvProcessor` and `BaseModelTool`.
