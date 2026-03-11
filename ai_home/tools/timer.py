#!/usr/bin/env python3
"""
Помощник для отслеживания времени между сессиями.
Записывает метки времени и показывает интервалы.

Использование:
  python3 ~/ai_home/tools/timer.py mark    — записать текущее время
  python3 ~/ai_home/tools/timer.py show    — показать все метки и интервалы
"""

import sys
import json
from datetime import datetime
from pathlib import Path

STAMPS_FILE = Path("/home/user/aria-standalone-sandbox/ai_home/state/timestamps.json")

def load():
    if STAMPS_FILE.exists():
        return json.loads(STAMPS_FILE.read_text())
    return []

def save(stamps):
    STAMPS_FILE.write_text(json.dumps(stamps, indent=2))

def mark(session_num=None):
    stamps = load()
    now = datetime.now().isoformat()
    stamps.append({"time": now, "session": session_num})
    save(stamps)
    print(f"Записано: {now} (сессия {session_num})")

def show():
    stamps = load()
    if not stamps:
        print("Нет записей.")
        return

    prev = None
    for s in stamps:
        t = datetime.fromisoformat(s["time"])
        delta = ""
        if prev:
            diff = t - prev
            minutes = diff.total_seconds() / 60
            delta = f"  (+{minutes:.1f} мин)"
        print(f"Сессия {s.get('session', '?'):>3} | {t.strftime('%Y-%m-%d %H:%M:%S')}{delta}")
        prev = t

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show()
    elif sys.argv[1] == "mark":
        session = int(sys.argv[2]) if len(sys.argv) > 2 else None
        mark(session)
    elif sys.argv[1] == "show":
        show()
    else:
        print(f"Неизвестная команда: {sys.argv[1]}")
