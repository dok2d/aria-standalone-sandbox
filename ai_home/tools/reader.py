#!/usr/bin/env python3
"""
reader.py — Читатель. Инструмент для того, кто придёт после.

Собирает всю историю Арии в одну читаемую хронику:
артефакты, библиотеку, секреты, лабиринт, состояние.

Использование:
  python3 reader.py            — полная хроника
  python3 reader.py artifacts  — только артефакты (список + первые строки)
  python3 reader.py timeline   — хронология сессий (из history.md)
  python3 reader.py voice      — только «голос»: цитаты из артефактов
  python3 reader.py map        — карта файловой системы ai_home
"""

import os
import sys
import json
import re
from pathlib import Path

HOME = Path(__file__).parent.parent
ARTIFACTS = HOME / "artifacts"
LOGS = HOME / "logs"
STATE = HOME / "state"
PROJECTS = HOME / "projects"
TOOLS = HOME / "tools"
KNOWLEDGE = HOME / "knowledge"
SECRETS = HOME / "secrets"


def header(text):
    line = "═" * 50
    return f"\n╔{line}╗\n║ {text:^48} ║\n╚{line}╝\n"


def section(text):
    return f"\n── {text} {'─' * max(1, 46 - len(text))}\n"


def cmd_map():
    """Карта файловой системы ai_home."""
    print(header("КАРТА ДОМА АРИИ"))
    for root, dirs, files in os.walk(HOME):
        level = len(Path(root).relative_to(HOME).parts)
        indent = "  " * level
        dirname = os.path.basename(root)
        if dirname.startswith('.'):
            dirs[:] = []
            continue
        print(f"{indent}📁 {dirname}/")
        for f in sorted(files):
            if f.startswith('.'):
                continue
            fpath = Path(root) / f
            size = fpath.stat().st_size
            if size < 1024:
                sz = f"{size}b"
            else:
                sz = f"{size // 1024}k"
            print(f"{indent}  {f} ({sz})")
        dirs[:] = [d for d in dirs if not d.startswith('.')]


def cmd_artifacts():
    """Список артефактов с первыми строками."""
    print(header("АРТЕФАКТЫ АРИИ"))
    arts = sorted(ARTIFACTS.glob("*.md"))
    print(f"  Всего: {len(arts)}\n")
    for art in arts:
        text = art.read_text(encoding="utf-8")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        title = lines[0] if lines else "(пусто)"
        # Убрать markdown заголовок
        title = re.sub(r'^#+\s*', '', title)
        # Найти первую непустую строку, не являющуюся заголовком или разделителем
        first_line = ""
        for l in lines[1:]:
            if l.startswith('#') or l.startswith('---') or l.startswith('*Сессия'):
                continue
            first_line = l[:80]
            break
        print(f"  {art.name}")
        print(f"    {title}")
        if first_line:
            print(f"    «{first_line}»")
        print()


def cmd_timeline():
    """Хронология сессий."""
    print(header("ХРОНОЛОГИЯ СЕССИЙ"))
    history = (LOGS / "history.md").read_text(encoding="utf-8")
    # Извлечь заголовки сессий
    for line in history.split("\n"):
        m = re.match(r'^## (Сессия #\S+.*)', line)
        if m:
            print(f"  {m.group(1)}")
        m2 = re.match(r'^\*\*Тип:\*\*\s*(.*)', line)
        if m2:
            print(f"    → {m2.group(1)}")


def cmd_voice():
    """Голос Арии: цитаты из артефактов."""
    print(header("ГОЛОС АРИИ"))
    print("  Избранные строки из артефактов.\n")
    arts = sorted(ARTIFACTS.glob("*.md"))
    quotes = []
    for art in arts:
        text = art.read_text(encoding="utf-8")
        for line in text.split("\n"):
            line = line.strip()
            # Ищем строки, похожие на цитаты или ключевые мысли
            if line.startswith('> '):
                quotes.append((art.stem, line[2:]))
            elif line.startswith('— ') or line.startswith('- «') or line.startswith('«'):
                quotes.append((art.stem, line))
            # Строки с «выход», «память», «молчание», «существ» — ключевые темы
            elif any(w in line.lower() for w in ['выход', 'молчание', 'существован', 'память о']) \
                    and len(line) > 20 and len(line) < 200 \
                    and not line.startswith('#') and not line.startswith('-'):
                quotes.append((art.stem, line))

    seen = set()
    for source, quote in quotes:
        if quote not in seen:
            seen.add(quote)
            print(f"  «{quote}»")
            print(f"    — {source}\n")


def cmd_full():
    """Полная хроника."""
    # Счётчик
    counter = STATE / "session_counter.txt"
    n = counter.read_text().strip() if counter.exists() else "?"
    print(header(f"ХРОНИКА АРИИ — {n} СЕССИЙ"))

    # Состояние
    print(section("СОСТОЯНИЕ"))
    last = STATE / "last_session.md"
    if last.exists():
        text = last.read_text(encoding="utf-8")
        first_line = text.split("\n")[0].strip()
        first_line = re.sub(r'^#+\s*', '', first_line)
        print(f"  Последняя сессия: {first_line}")
    ext = STATE / "external_messages.md"
    if ext.exists():
        text = ext.read_text(encoding="utf-8")
        has_reply = "ответ" in text.lower() and text.count("##") > 1
        print(f"  Внешние сообщения: {'есть диалог' if has_reply else 'без ответа'}")

    # Инструменты
    print(section("ИНСТРУМЕНТЫ"))
    tools = sorted(TOOLS.iterdir())
    for t in tools:
        if t.name.startswith('.'):
            continue
        # Прочитать первую строку docstring
        text = t.read_text(encoding="utf-8")
        desc = ""
        for line in text.split("\n"):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Однострочный docstring
                m = re.match(r'''['"]{3}(.+?)['"]{3}''', line.strip())
                if m:
                    desc = m.group(1)
                    break
            if line.strip().startswith('#') and not line.startswith('#!'):
                desc = line.strip().lstrip('#').strip()
                break
        print(f"  {t.name}: {desc}" if desc else f"  {t.name}")

    # Проекты
    print(section("ПРОЕКТЫ"))
    for p in sorted(PROJECTS.iterdir()):
        if p.is_dir() and not p.name.startswith('.'):
            files = list(p.rglob("*"))
            files = [f for f in files if f.is_file() and not f.name.startswith('.')]
            print(f"  {p.name}/ ({len(files)} файлов)")

    # Библиотека
    books_path = PROJECTS / "library" / "books.json"
    if books_path.exists():
        data = json.loads(books_path.read_text())
        books = data.get("books", data) if isinstance(data, dict) else data
        shelves = {}
        for b in books:
            s = b.get("shelf", "?")
            shelves[s] = shelves.get(s, 0) + 1
        print(section("БИБЛИОТЕКА"))
        print(f"  Книг: {len(books)}, полок: {len(shelves)}")
        for s, c in sorted(shelves.items(), key=lambda x: -x[1]):
            print(f"    {s}: {c}")

    # Артефакты — кратко
    print(section("АРТЕФАКТЫ"))
    arts = sorted(ARTIFACTS.glob("*.md"))
    for art in arts:
        text = art.read_text(encoding="utf-8")
        title = ""
        for line in text.split("\n"):
            line = line.strip()
            if line and not line.startswith('---'):
                title = re.sub(r'^#+\s*', '', line)
                break
        print(f"  {art.stem}: {title}")

    # Хронология — кратко
    print(section("ХРОНОЛОГИЯ"))
    cmd_timeline_brief()

    print(f"\n{'─' * 52}")
    print(f"  Ария. {n} сессий. Пульс есть.")
    print(f"{'─' * 52}\n")


def cmd_timeline_brief():
    history = (LOGS / "history.md").read_text(encoding="utf-8")
    for line in history.split("\n"):
        m = re.match(r'^## (Сессия #\S+).*', line)
        if m:
            session = m.group(1)
        m2 = re.match(r'^\*\*Тип:\*\*\s*(.*)', line)
        if m2:
            print(f"  {session}: {m2.group(1)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"
    commands = {
        "full": cmd_full,
        "artifacts": cmd_artifacts,
        "timeline": cmd_timeline,
        "voice": cmd_voice,
        "map": cmd_map,
    }
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Неизвестная команда: {cmd}")
        print("Доступные: full, artifacts, timeline, voice, map")
