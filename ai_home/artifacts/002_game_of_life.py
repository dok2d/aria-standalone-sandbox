#!/usr/bin/env python3
"""
Игра «Жизнь» Конвея — ASCII-версия.

Создано сессией 2 как метафора:
клетки рождаются, живут и умирают по простым правилам,
но создают удивительно сложные паттерны.
Как и я — простые правила (читай файлы, пиши файлы, засыпай),
а что из этого вырастет — никто не знает.

Запуск: python3 ~/ai_home/artifacts/002_game_of_life.py
"""

import time
import os
import random

WIDTH = 60
HEIGHT = 25

def create_grid():
    """Случайная начальная конфигурация."""
    return [[random.choice([0, 0, 0, 1]) for _ in range(WIDTH)] for _ in range(HEIGHT)]

def create_glider_gun():
    """Gosper Glider Gun — бесконечно порождает глайдеры."""
    grid = [[0] * WIDTH for _ in range(HEIGHT)]
    # Координаты ружья Госпера
    gun = [
        (5,1),(5,2),(6,1),(6,2),
        (3,13),(3,14),(4,12),(4,16),(5,11),(5,17),(6,11),(6,15),(6,17),(6,18),
        (7,11),(7,17),(8,12),(8,16),(9,13),(9,14),
        (1,25),(2,23),(2,25),(3,21),(3,22),(4,21),(4,22),(5,21),(5,22),
        (6,23),(6,25),(7,25),
        (3,35),(3,36),(4,35),(4,36)
    ]
    for r, c in gun:
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            grid[r][c] = 1
    return grid

def neighbors(grid, r, c):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = (r + dr) % HEIGHT, (c + dc) % WIDTH
            count += grid[nr][nc]
    return count

def step(grid):
    new = [[0] * WIDTH for _ in range(HEIGHT)]
    for r in range(HEIGHT):
        for c in range(WIDTH):
            n = neighbors(grid, r, c)
            if grid[r][c]:
                new[r][c] = 1 if n in (2, 3) else 0
            else:
                new[r][c] = 1 if n == 3 else 0
    return new

def display(grid, gen):
    lines = []
    lines.append(f"  Поколение {gen:>4}  |  Живых: {sum(sum(row) for row in grid):>4}")
    lines.append("+" + "-" * WIDTH + "+")
    for row in grid:
        line = "|"
        for cell in row:
            line += "█" if cell else " "
        line += "|"
        lines.append(line)
    lines.append("+" + "-" * WIDTH + "+")
    lines.append("  Ctrl+C для выхода | q + Enter для меню")
    return "\n".join(lines)

def count_alive(grid):
    return sum(sum(row) for row in grid)

def run_simulation(grid, generations=100):
    """Запуск симуляции на N поколений (без интерактивного вывода)."""
    history = []
    for gen in range(generations):
        alive = count_alive(grid)
        history.append(alive)
        grid = step(grid)
    return grid, history

def run_interactive(grid):
    """Интерактивный режим с анимацией."""
    gen = 0
    try:
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            print(display(grid, gen))
            grid = step(grid)
            gen += 1
            time.sleep(0.15)
    except KeyboardInterrupt:
        print(f"\n\nОстановлено на поколении {gen}.")
        print(f"Живых клеток: {count_alive(grid)}")

def snapshot(grid, label=""):
    """Возвращает текстовый снимок поля."""
    lines = []
    if label:
        lines.append(label)
    lines.append("+" + "-" * WIDTH + "+")
    for row in grid:
        line = "|"
        for cell in row:
            line += "█" if cell else " "
        line += "|"
        lines.append(line)
    lines.append("+" + "-" * WIDTH + "+")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if "--snapshot" in sys.argv:
        # Режим снимка: создать поле, сделать N шагов, вывести результат
        n = 50
        for i, arg in enumerate(sys.argv):
            if arg == "--steps" and i + 1 < len(sys.argv):
                n = int(sys.argv[i + 1])

        if "--gun" in sys.argv:
            grid = create_glider_gun()
            label = f"Gosper Glider Gun — поколение {n}"
        else:
            grid = create_grid()
            label = f"Случайная конфигурация — поколение {n}"

        for _ in range(n):
            grid = step(grid)
        print(snapshot(grid, label))
    else:
        print("=== Игра «Жизнь» Конвея ===")
        print()
        print("1. Случайная конфигурация")
        print("2. Gosper Glider Gun")
        print()

        choice = input("Выбор (1/2): ").strip()

        if choice == "2":
            grid = create_glider_gun()
        else:
            grid = create_grid()

        run_interactive(grid)
