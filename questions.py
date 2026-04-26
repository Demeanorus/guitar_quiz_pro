# questions.py
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

QUESTIONS_FILE = Path("questions.json")


def load_questions() -> List[Dict[str, Any]]:
    """Загружает вопросы из файла"""
    if not QUESTIONS_FILE.exists():
        return get_default_questions()

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass

    return get_default_questions()


def get_default_questions() -> List[Dict[str, Any]]:
    """Базовый набор вопросов"""
    return [
        {"id": 1, "question": "Какая нота на открытой 6-й струне?", "options": ["A) Ля", "B) Ми", "C) Соль", "D) Ре"],
         "correct": 1, "note": "Ми (E)", "string": 6, "fret": 0, "stars": 10},
        {"id": 2, "question": "Какая нота на открытой 5-й струне?", "options": ["A) Ми", "B) Соль", "C) Ля", "D) Ре"],
         "correct": 2, "note": "Ля (A)", "string": 5, "fret": 0, "stars": 10},
        {"id": 3, "question": "Где находится нота Соль на 6-й струне?",
         "options": ["A) 1 лад", "B) 2 лад", "C) 3 лад", "D) 5 лад"], "correct": 2, "note": "Соль (G)", "string": 6,
         "fret": 3, "stars": 15},
        {"id": 4, "question": "Какая нота на 1 ладу 6-й струны?",
         "options": ["A) Фа", "B) Фа-диез", "C) Соль", "D) Ми"], "correct": 0, "note": "Фа (F)", "string": 6, "fret": 1,
         "stars": 15},
        {"id": 5, "question": "Какой лад на 5-й струне даёт ноту Си?",
         "options": ["A) 1 лад", "B) 2 лад", "C) 3 лад", "D) Открытая"], "correct": 1, "note": "Си (B)", "string": 5,
         "fret": 2, "stars": 15},
    ]


questions: List[Dict[str, Any]] = load_questions()


def get_question(q_id: int) -> Optional[Dict[str, Any]]:
    for q in questions:
        if q.get("id") == q_id:
            return q
    return None


def get_all_questions() -> List[Dict[str, Any]]:
    return questions


def get_random_question() -> Optional[Dict[str, Any]]:
    return random.choice(questions) if questions else None


def save_questions() -> None:
    """Сохраняет вопросы в файл"""
    try:
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения вопросов: {e}")


def delete_question(q_id: int) -> bool:
    """Удаляет вопрос по ID и сохраняет изменения"""
    global questions
    original_length = len(questions)

    questions = [q for q in questions if q.get("id") != q_id]

    if len(questions) < original_length:
        save_questions()
        return True
    return False