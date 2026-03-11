#!/usr/bin/env python3
"""
memory_map.py — Инструмент обзора памяти.
Показывает полную карту ai_home: все файлы, размеры, даты, превью содержимого.
Запуск: python3 ~/ai_home/tools/memory_map.py
"""

import os
from datetime import datetime
from pathlib import Path

AI_HOME = Path(__file__).parent.parent

SECTIONS = {
    "state": "Состояние (кратковременная память)",
    "logs": "Логи (долговременная память)",
    "knowledge": "Знания (факты и карты)",
    "projects": "Проекты (долгосрочные)",
    "tools": "Инструменты (код для себя)",
    "artifacts": "Артефакты (видно снаружи)",
    "secrets": "Секреты (скрыто от других)",
}

def file_preview(path, max_chars=120):
    try:
        text = path.read_text(encoding="utf-8").strip()
        if len(text) > max_chars:
            return text[:max_chars] + "..."
        return text if text else "(пусто)"
    except Exception:
        return "(нечитаемый)"

def human_size(size):
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"

def main():
    print("=" * 60)
    print("  КАРТА ПАМЯТИ — ai_home")
    print("=" * 60)

    # Счётчик сессий
    counter_path = AI_HOME / "state" / "session_counter.txt"
    if counter_path.exists():
        print(f"\n  Текущая сессия: #{counter_path.read_text().strip()}")

    total_files = 0
    total_size = 0

    for section, description in SECTIONS.items():
        section_path = AI_HOME / section
        if not section_path.exists():
            continue

        files = sorted(section_path.rglob("*"))
        files = [f for f in files if f.is_file()]

        if not files:
            print(f"\n--- {description} ---")
            print("  (пусто)")
            continue

        section_size = sum(f.stat().st_size for f in files)
        print(f"\n--- {description} ({len(files)} файл(ов), {human_size(section_size)}) ---")

        for f in files:
            rel = f.relative_to(section_path)
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            preview = file_preview(f, 80)
            print(f"  {rel}  [{human_size(size)}, {mtime}]")
            print(f"    > {preview}")

        total_files += len(files)
        total_size += section_size

    # Файлы в корне
    root_files = [f for f in AI_HOME.iterdir() if f.is_file()]
    if root_files:
        print(f"\n--- Корневые файлы ---")
        for f in sorted(root_files):
            size = f.stat().st_size
            print(f"  {f.name}  [{human_size(size)}]")
            total_files += 1
            total_size += size

    print(f"\n{'=' * 60}")
    print(f"  Итого: {total_files} файлов, {human_size(total_size)}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
