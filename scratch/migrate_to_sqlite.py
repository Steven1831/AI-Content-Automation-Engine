
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from flows.image_content_generator.pipeline.storage_csv import CsvStore
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore

CSV_PATH = Path("flows/image_content_generator/out_short/ideas_tracking.csv")
DB_PATH = Path("flows/image_content_generator/out_short/ideas_tracking.db")

def migrate():
    if not CSV_PATH.exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    print(f"Migrating data from {CSV_PATH} to {DB_PATH}...")
    
    csv_store = CsvStore(CSV_PATH)
    sqlite_store = SqliteStore(DB_PATH)
    
    # Read all from CSV
    df = csv_store.read_all()
    ideas = []
    for _, row in df.iterrows():
        ideas.append(csv_store._map_row(row))
    
    # Save to SQLite
    sqlite_store.migrate_from_csv(ideas)
    
    print(f"Successfully migrated {len(ideas)} records.")
    print(f"IMPORTANT: You can now use the SQLite store.")

if __name__ == "__main__":
    migrate()
