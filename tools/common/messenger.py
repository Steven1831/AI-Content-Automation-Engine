import datetime
from pathlib import Path
from pydantic import BaseModel


class Messenger:
    """
    Standardized tool for terminal feedback and file logging.
    """
    LOG_FILE: Path = Path("flows/image_content_generator/production.log")

    @staticmethod
    def _log(level: str, message: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(message)
        
        # Ensure directory exists
        Messenger.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Messenger.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    @staticmethod
    def info(message: str) -> None:
        Messenger._log("INFO", message)

    @staticmethod
    def success(message: str) -> None:
        Messenger._log("SUCCESS", f"SUCCESS: {message}")

    @staticmethod
    def step_success(message: str) -> None:
        Messenger._log("STEP", f"STEP SUCCESS: {message}")

    @staticmethod
    def warning(message: str) -> None:
        Messenger._log("WARNING", f"WARNING: {message}")

    @staticmethod
    def error(message: str) -> None:
        Messenger._log("ERROR", f"ERROR: {message}")

    @staticmethod
    def image(message: str) -> None:
        Messenger._log("IMAGE", f"IMAGE: {message}")

    @staticmethod
    def audio(message: str) -> None:
        Messenger._log("AUDIO", f"AUDIO: {message}")

    @staticmethod
    def usage(model: str, prompt: int, thoughts: int, output: int, total: int) -> None:
        report = (
            f"\n[Usage Report: {model}]\n"
            f"   +- Prompt: {prompt}\n"
            f"   +- Thoughts: {thoughts}\n"
            f"   +- Output: {output}\n"
            f"   +- Total Tokens: {total}\n"
        )
        Messenger._log("USAGE", report)
