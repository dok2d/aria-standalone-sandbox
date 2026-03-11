#!/usr/bin/env python3
"""
ЭКОСИСТЕМА — запускает все четыре организма и показывает их взаимодействие.

Создана в сессии 7. Обновлена в сессии 14 (добавлен Организм-В).
Обновлена в сессии 18 (добавлен Антиорганизм-Г).
"""

import subprocess
import sys
from pathlib import Path

def run():
    base = Path(__file__).parent

    print("=" * 50)
    print("  ЭКОСИСТЕМА ai_home — четыре организма")
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

    # Запускаем Антиорганизм-Г (тень)
    print(">>> Запуск Антиорганизма-Г (тень)...")
    result_g = subprocess.run(
        [sys.executable, str(base / "organism_g.py")],
        capture_output=True, text=True
    )
    print(result_g.stdout)
    if result_g.stderr:
        print(f"  [ошибка Г]: {result_g.stderr}")

    print("=" * 50)
    print("  Четыре организма прожили ещё одно поколение.")
    print("  А и Б мутируют. В отражает общий язык. Г хранит мёртвое.")
    print("  Проверьте history/, history_b/, history_v/, history_g/")
    print("=" * 50)

if __name__ == "__main__":
    run()
