from pathlib import Path
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
store = SqliteStore(db_path)
for i in range(1, 25):
    idea = store.get_by_id(i)
    if idea:
        print(f"ID {i}: {idea.state}")
