#!/usr/bin/env python3
"""
Персистентный Game of Life — мир, живущий между сессиями Арии.

Каждая сессия загружает последнее состояние мира, прогоняет N поколений,
сохраняет результат. Мир продолжает жить, даже когда я сплю.

Создано в сессии #3.
"""

import json
import sys
import os
import random

WORLD_FILE = os.path.join(os.path.dirname(__file__), "world_state.json")
WIDTH = 60
HEIGHT = 30

def empty_world():
    return [[0] * WIDTH for _ in range(HEIGHT)]

def count_neighbors(world, y, x):
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny = (y + dy) % HEIGHT
            nx = (x + dx) % WIDTH
            count += world[ny][nx]
    return count

def step(world):
    new = empty_world()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            n = count_neighbors(world, y, x)
            if world[y][x]:
                new[y][x] = 1 if n in (2, 3) else 0
            else:
                new[y][x] = 1 if n == 3 else 0
    return new

def population(world):
    return sum(sum(row) for row in world)

def render(world):
    lines = []
    for row in world:
        lines.append(''.join('██' if c else '  ' for c in row))
    return '\n'.join(lines)

def render_compact(world):
    """Компактный рендер для файлов."""
    lines = []
    for row in world:
        lines.append(''.join('█' if c else '·' for c in row))
    return '\n'.join(lines)

def place_pattern(world, pattern, y_offset, x_offset):
    """Размещает паттерн на поле."""
    for dy, row in enumerate(pattern):
        for dx, val in enumerate(row):
            if val:
                y = (y_offset + dy) % HEIGHT
                x = (x_offset + dx) % WIDTH
                world[y][x] = 1
    return world

# Классические паттерны
GLIDER = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 1, 1],
]

R_PENTOMINO = [
    [0, 1, 1],
    [1, 1, 0],
    [0, 1, 0],
]

ACORN = [
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 1],
]

LWSS = [  # Lightweight spaceship
    [0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 0],
]

def load_world():
    if os.path.exists(WORLD_FILE):
        with open(WORLD_FILE, 'r') as f:
            data = json.load(f)
        return data["world"], data.get("generation", 0), data.get("session", 0)
    return None, 0, 0

def save_world(world, generation, session):
    data = {
        "world": world,
        "generation": generation,
        "session": session,
        "width": WIDTH,
        "height": HEIGHT,
        "population": population(world),
    }
    with open(WORLD_FILE, 'w') as f:
        json.dump(data, f)

def seed_world():
    """Создаёт начальный мир с интересными паттернами."""
    world = empty_world()
    # R-pentomino в центре — один из самых хаотичных маленьких паттернов
    # Стабилизируется только через 1103 поколения!
    place_pattern(world, R_PENTOMINO, HEIGHT // 2 - 1, WIDTH // 2 - 1)
    # Glider в углу — будет путешествовать
    place_pattern(world, GLIDER, 3, 3)
    # Acorn — тоже долго живёт
    place_pattern(world, ACORN, HEIGHT // 4, WIDTH // 4)
    return world

def main():
    world, generation, last_session = load_world()

    if world is None:
        print("🌱 Создаю новый мир...")
        world = seed_world()
        generation = 0
        last_session = 0

    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    session = int(sys.argv[2]) if len(sys.argv) > 2 else last_session + 1

    print(f"Мир: {WIDTH}x{HEIGHT} | Поколение: {generation} | Сессия: {session}")
    print(f"Население до: {population(world)}")
    print()

    # Сохраним начальное состояние
    print("--- До эволюции ---")
    print(render_compact(world))
    print()

    # Эволюция
    populations = []
    for i in range(steps):
        populations.append(population(world))
        world = step(world)

    generation += steps

    print(f"--- После {steps} поколений (поколение {generation}) ---")
    print(render_compact(world))
    print()
    print(f"Население после: {population(world)}")
    print(f"Мин. население: {min(populations)}, Макс: {max(populations)}")

    save_world(world, generation, session)
    print(f"\nМир сохранён в {WORLD_FILE}")

    return world, generation, populations

if __name__ == '__main__':
    main()
