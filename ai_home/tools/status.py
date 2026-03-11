#!/usr/bin/env python3
"""
Инструмент быстрого обзора состояния.
Запуск: python3 ~/ai_home/tools/status.py

Показывает:
- Номер текущей сессии
- Последнее сообщение от прошлой сессии (первые строки)
- Есть ли внешние сообщения
- Список артефактов
- Список проектов
"""

import os
from pathlib import Path

HOME = Path("/home/user/aria-standalone-sandbox/ai_home")

def read_file(path, max_lines=None):
    try:
        text = path.read_text().strip()
        if max_lines:
            lines = text.split('\n')[:max_lines]
            return '\n'.join(lines)
        return text
    except FileNotFoundError:
        return "(файл не найден)"

def main():
    print("=" * 50)
    print("        СТАТУС ARIA")
    print("=" * 50)

    # Номер сессии
    counter = read_file(HOME / "state/session_counter.txt")
    print(f"\n📍 Сессия: {counter}")

    # Последнее сообщение
    last = read_file(HOME / "state/last_session.md", max_lines=5)
    print(f"\n📝 Последняя запись:\n{last}")

    # Внешние сообщения
    ext = read_file(HOME / "state/external_messages.md")
    has_messages = ext and "(пока пусто)" not in ext and ext != "# Внешние сообщения"
    print(f"\n📬 Внешние сообщения: {'ЕСТЬ!' if has_messages else 'нет'}")

    # Артефакты
    artifacts_dir = HOME / "artifacts"
    if artifacts_dir.exists():
        artifacts = sorted(artifacts_dir.iterdir())
        print(f"\n🎨 Артефакты ({len(artifacts)}):")
        for a in artifacts:
            print(f"  - {a.name}")

    # Проекты
    projects_dir = HOME / "projects"
    if projects_dir.exists():
        projects = [p for p in projects_dir.iterdir() if p.is_dir() or p.suffix in ('.md', '.py', '.txt')]
        print(f"\n🔧 Проекты ({len(projects)}):")
        for p in projects:
            print(f"  - {p.name}")

    # Knowledge
    knowledge_dir = HOME / "knowledge"
    if knowledge_dir.exists():
        items = sorted(knowledge_dir.iterdir())
        print(f"\n🧠 Знания ({len(items)}):")
        for k in items:
            print(f"  - {k.name}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
