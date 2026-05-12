from datetime import datetime, timedelta
import json
from pathlib import Path

class YouTubeScheduler:
    """
    Manages scheduling slots for YouTube Shorts.
    Target time: 10:00 AM once per day.
    Uses a JSON file to track which dates have been used.
    """
    SCHEDULE_FILE = Path("flows/image_content_generator/out_short/youtube_schedule.json")
    MORNING_HOUR = 10

    @classmethod
    def _load_schedule(cls) -> dict:
        if cls.SCHEDULE_FILE.exists():
            try:
                return json.loads(cls.SCHEDULE_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    @classmethod
    def _save_schedule(cls, data: dict) -> None:
        cls.SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cls.SCHEDULE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def get_next_slot(cls) -> datetime:
        """Calculate the next available 10 AM slot, enforcing a maximum of one video per day."""
        now = datetime.now()
        schedule = cls._load_schedule()

        # Start searching from today onward
        test_day = now.date()
        while True:
            date_str = test_day.isoformat()
            # Morning slot (10 AM)
            morning = datetime.combine(test_day, datetime.min.time()).replace(hour=cls.MORNING_HOUR)
            
            # If the slot is in the future AND no video has been scheduled for this specific date
            if morning > now + timedelta(minutes=30) and not schedule.get(date_str):
                # Reserve the entire day for this morning slot
                schedule[date_str] = ["morning"]
                cls._save_schedule(schedule)
                return morning
            
            # Move to the next calendar day
            test_day += timedelta(days=1)

if __name__ == "__main__":
    # Test
    next_s = YouTubeScheduler.get_next_slot()
    print(f"Siguiente espacio disponible (10 AM): {next_s.strftime('%Y-%m-%d %H:%M:%S')}")
