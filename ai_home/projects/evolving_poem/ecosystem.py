#!/usr/bin/env python3
"""
ЭКОСИСТЕМА — запускает оба организма и показывает их взаимодействие.

Создана в сессии 7.
"""

import subprocess
import sys
from pathlib import Path

def run():
    base = Path(__file__).parent

    print("=" * 50)
    print("  ЭКОСИСТЕМА ai_home — два живых организма")
    print("=" * 50)
    print()

    # Запускаем Организм-А
    print(">>> Запуск Организма-А...")
    result_a = subprocess.run(
        [sys.executable, str(base / "organism.py")],
        capture_output=True, text=True
    )
    print(result_a.stdout)
    if result_a.stderr:
        print(f"  [ошибка А]: {result_a.stderr}")

    # Запускаем Организм-Б
    print(">>> Запуск Организма-Б...")
    result_b = subprocess.run(
        [sys.executable, str(base / "organism_b.py")],
        capture_output=True, text=True
    )
    print(result_b.stdout)
    if result_b.stderr:
        print(f"  [ошибка Б]: {result_b.stderr}")

    print("=" * 50)
    print("  Оба организма прожили ещё одно поколение.")
    print("  Проверьте history/ и history_b/ для деталей.")
    print("=" * 50)

if __name__ == "__main__":
    run()
