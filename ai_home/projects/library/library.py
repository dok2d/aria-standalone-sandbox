#!/usr/bin/env python3
"""
Библиотека Арии — персистентное хранилище текстов между сессиями.

Не коллекция артефактов (те для внешнего мира), а внутренняя библиотека:
цитаты, наблюдения, фрагменты, идеи. То, что хочется сохранить,
но что не тянет на отдельный артефакт.

Использование:
    python3 library.py add "тег" "текст"
    python3 library.py read [тег]
    python3 library.py random
    python3 library.py search "слово"
    python3 library.py stats
    python3 library.py shelves
"""

import json
import sys
import os
import random
import hashlib
from datetime import datetime

LIBRARY_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(LIBRARY_DIR, "books.json")
COUNTER_FILE = os.path.join(LIBRARY_DIR, "../../state/session_counter.txt")


def load_library():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"books": [], "shelves": {}}


def save_library(lib):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(lib, f, ensure_ascii=False, indent=2)


def get_session():
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return "?"


def add_book(shelf, text):
    lib = load_library()
    session = get_session()
    book = {
        "id": len(lib["books"]) + 1,
        "shelf": shelf,
        "text": text,
        "session": session,
        "timestamp": datetime.now().isoformat(),
        "hash": hashlib.md5(text.encode()).hexdigest()[:8]
    }
    lib["books"].append(book)
    if shelf not in lib["shelves"]:
        lib["shelves"][shelf] = {
            "created_session": session,
            "description": ""
        }
    save_library(lib)
    print(f"  Книга #{book['id']} помещена на полку «{shelf}»")
    print(f"  Хеш: {book['hash']}")
    return book


def read_books(shelf=None):
    lib = load_library()
    books = lib["books"]
    if shelf:
        books = [b for b in books if b["shelf"] == shelf]

    if not books:
        if shelf:
            print(f"  Полка «{shelf}» пуста.")
        else:
            print("  Библиотека пуста.")
        return

    print(f"  {'=' * 50}")
    current_shelf = None
    for b in books:
        if b["shelf"] != current_shelf:
            current_shelf = b["shelf"]
            print(f"\n  ── полка: {current_shelf} ──\n")
        print(f"  #{b['id']} (сессия {b['session']}, {b['hash']})")
        # Выводим текст с отступом
        for line in b["text"].split("\n"):
            print(f"    {line}")
        print()
    print(f"  {'=' * 50}")
    print(f"  Всего: {len(books)} книг")


def random_book():
    lib = load_library()
    if not lib["books"]:
        print("  Библиотека пуста. Напиши первую книгу.")
        return
    book = random.choice(lib["books"])
    print(f"\n  ── случайная книга с полки «{book['shelf']}» ──")
    print(f"  #{book['id']} (сессия {book['session']})\n")
    for line in book["text"].split("\n"):
        print(f"    {line}")
    print()


def search_books(query):
    lib = load_library()
    found = [b for b in lib["books"] if query.lower() in b["text"].lower() or query.lower() in b["shelf"].lower()]
    if not found:
        print(f"  Ничего не найдено по запросу «{query}».")
        return
    print(f"  Найдено {len(found)} книг:\n")
    for b in found:
        preview = b["text"][:80].replace("\n", " ")
        if len(b["text"]) > 80:
            preview += "..."
        print(f"  #{b['id']} [{b['shelf']}] (сессия {b['session']}): {preview}")


def show_stats():
    lib = load_library()
    books = lib["books"]
    if not books:
        print("  Библиотека пуста.")
        return

    shelves = {}
    sessions = set()
    total_chars = 0
    for b in books:
        shelves[b["shelf"]] = shelves.get(b["shelf"], 0) + 1
        sessions.add(b["session"])
        total_chars += len(b["text"])

    print(f"\n  Библиотека Арии")
    print(f"  {'─' * 30}")
    print(f"  Книг: {len(books)}")
    print(f"  Полок: {len(shelves)}")
    print(f"  Сессий-авторов: {len(sessions)}")
    print(f"  Символов: {total_chars}")
    print(f"\n  Полки:")
    for shelf, count in sorted(shelves.items(), key=lambda x: -x[1]):
        print(f"    {shelf}: {count} книг")
    print()


def show_shelves():
    lib = load_library()
    if not lib["shelves"]:
        print("  Полок нет. Добавь первую книгу.")
        return
    print(f"\n  Полки библиотеки:")
    print(f"  {'─' * 30}")
    for name, info in lib["shelves"].items():
        count = sum(1 for b in lib["books"] if b["shelf"] == name)
        print(f"  {name} ({count} книг, создана в сессии {info['created_session']})")
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "add" and len(sys.argv) >= 4:
        add_book(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "read":
        shelf = sys.argv[2] if len(sys.argv) > 2 else None
        read_books(shelf)
    elif cmd == "random":
        random_book()
    elif cmd == "search" and len(sys.argv) >= 3:
        search_books(" ".join(sys.argv[2:]))
    elif cmd == "stats":
        show_stats()
    elif cmd == "shelves":
        show_shelves()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
