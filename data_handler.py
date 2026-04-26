# data_handler.py
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

DATA_FILE = Path("progress.json")
VERSION = 2


def load_progress() -> Dict[str, Any]:
    """Загружает прогресс с авто-восстановлением"""
    default = {
        "version": VERSION,
        "total_stars": 0,
        "correct_answers": 0,
        "total_questions_answered": 0,
        "lives": 5,
        "wrong_answers": [],
        "streak": 0,
        "hero_level": "Новичок 🌱",
        "last_saved": datetime.now().isoformat()
    }

    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("version") == VERSION:
                # Добавляем отсутствующие ключи
                for key, value in default.items():
                    data.setdefault(key, value)
                return data
    except Exception as e:
        print(f"⚠️ Ошибка загрузки прогресса: {e}")

    return default


def save_progress(progress: Dict[str, Any]) -> None:
    """Сохраняет прогресс"""
    try:
        data_to_save = progress.copy()
        data_to_save["version"] = VERSION
        data_to_save["last_saved"] = datetime.now().isoformat()

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")