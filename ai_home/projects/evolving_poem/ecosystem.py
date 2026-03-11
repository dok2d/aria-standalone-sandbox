#!/usr/bin/env python3
"""
ЭКОСИСТЕМА — запускает все три организма и показывает их взаимодействие.

Создана в сессии 7. Обновлена в сессии 14 (добавлен Организм-В).
"""

import subprocess
import sys
from pathlib import Path

def run():
    base = Path(__file__).parent

    print("=" * 50)
    print("  ЭКОСИСТЕМА ai_home — три живых организма")
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

    # Запускаем Организм-В (мост)
    print(">>> Запуск Организма-В (мост)...")
    result_v = subprocess.run(
        [sys.executable, str(base / "organism_v.py")],
        capture_output=True, text=True
    )
    print(result_v.stdout)
    if result_v.stderr:
        print(f"  [ошибка В]: {result_v.stderr}")

    print("=" * 50)
    print("  Три организма прожили ещё одно поколение.")
    print("  А и Б мутируют. В отражает их общий язык.")
    print("  Проверьте history/, history_b/, history_v/")
    print("=" * 50)

if __name__ == "__main__":
    run()
