
import sqlite3
from pathlib import Path
from typing import List, Optional
from flows.image_content_generator.pipeline.schemas import IdeaRaw, State

class SqliteStore:
    """
    SQLite implementation of the production tracking storage.
    Eliminates file locking issues on Windows.
    """
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    state TEXT NOT NULL,
                    category TEXT,
                    drive_file_id TEXT,
                    youtube_video_id TEXT
                )
            """)
            # Migration: Add columns if they don't exist in an old DB
            try:
                conn.execute("ALTER TABLE ideas ADD COLUMN drive_file_id TEXT")
            except sqlite3.OperationalError:
                pass # Already exists
            try:
                conn.execute("ALTER TABLE ideas ADD COLUMN youtube_video_id TEXT")
            except sqlite3.OperationalError:
                pass # Already exists
            
            conn.commit()

    def _row_to_obj(self, row) -> IdeaRaw:
        return IdeaRaw(
            id=row[0], 
            title=row[1], 
            state=State(row[2]), 
            category=row[3],
            drive_file_id=row[4],
            youtube_video_id=row[5]
        )

    def get_by_id(self, idea_id: int) -> Optional[IdeaRaw]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, title, state, category, drive_file_id, youtube_video_id FROM ideas WHERE id = ?", (idea_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_obj(row)
        return None

    def get_first_by_state(self, state: State) -> Optional[IdeaRaw]:
        results = self.get_all_by_state(state, limit=1)
        return results[0] if results else None

    def get_all_by_state(self, state: State, limit: int = 10) -> List[IdeaRaw]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, title, state, category, drive_file_id, youtube_video_id FROM ideas WHERE state = ? ORDER BY id ASC LIMIT ?", (state.value, limit))
            return [self._row_to_obj(row) for row in cursor.fetchall()]

    def get_all(self) -> List[IdeaRaw]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, title, state, category, drive_file_id, youtube_video_id FROM ideas ORDER BY id ASC")
            return [self._row_to_obj(row) for row in cursor.fetchall()]

    def add_new_idea(self, title: str, category: str) -> IdeaRaw:
        next_id = self.get_next_id()
        with sqlite3.connect(self.db_path) as conn:
            # Check if title exists
            cursor = conn.execute("SELECT id FROM ideas WHERE title = ?", (title,))
            if cursor.fetchone():
                title = f"{title} #{next_id}"
            
            conn.execute("INSERT INTO ideas (id, title, state, category) VALUES (?, ?, ?, ?)", 
                         (next_id, title, State.NEW.value, category))
            conn.commit()
            return IdeaRaw(id=next_id, title=title, state=State.NEW.value, category=category)

    def get_next_id(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT MAX(id) FROM ideas")
            max_id = cursor.fetchone()[0]
            return (max_id or 0) + 1

    def save(self, idea_obj: IdeaRaw) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE ideas 
                SET title = ?, state = ?, category = ?, drive_file_id = ?, youtube_video_id = ? 
                WHERE id = ?
            """, 
            (idea_obj.title, idea_obj.state.value, idea_obj.category, idea_obj.drive_file_id, idea_obj.youtube_video_id, idea_obj.id))
            conn.commit()

    def migrate_from_csv(self, csv_data: List[IdeaRaw]):
        """Helper to populate from existing CSV data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM ideas")
            for idea in csv_data:
                conn.execute("INSERT INTO ideas (id, title, state, category, drive_file_id, youtube_video_id) VALUES (?, ?, ?, ?, ?, ?)", 
                             (idea.id, idea.title, idea.state.value, idea.category, idea.drive_file_id, idea.youtube_video_id))
            conn.commit()
