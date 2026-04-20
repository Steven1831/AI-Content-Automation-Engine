# Onboarding Checklist

The master guide for creating a new video automation project.

## 1. Bootstrap Structure
```bash
mkdir -p flows/<app_id>/pipeline flows/<app_id>/out flows/<app_id>/resource
touch flows/<app_id>/__init__.py flows/<app_id>/pipeline/__init__.py
```

## 2. Implement Core Layer
1. Define `State` and data models in `schemas.py`.
2. Implement `CsvStore` in `storage_csv.py` (Refer to `04_persistence_state.md`).
3. Setup `main.py` entry point (Refer to `01_architecture_patterns.md`).

## 3. Logic Implementation
1. Create `Pipeline` class in `pipeline.py` inheriting from `BaseModelTool`.
2. Implement granular methods following the documentation standards in `03_documentation_logging.md`.

## 4. Tools Integration
- Import generators (Gemini, FFmpeg) from the `tools/` package.
- Always use the `Messenger` for feedback.

## 5. Deployment
1. Add necessary environment variables to `.env`.
2. Verify execution via the `main.py` CLI.
