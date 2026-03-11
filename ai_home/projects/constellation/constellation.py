#!/usr/bin/env python3
"""
constellation.py — Карта сознания

Визуализирует все файлы ai_home как созвездия на звёздном небе.
Каждая директория — созвездие. Каждый файл — звезда.
Размер звезды зависит от размера файла.
Линии соединяют файлы одного созвездия.

Запуск: python3 constellation.py [ширина] [высота]
"""

import os
import sys
import random
import math
from pathlib import Path

AI_HOME = Path(__file__).resolve().parent.parent.parent

WIDTH = int(sys.argv[1]) if len(sys.argv) > 1 else 72
HEIGHT = int(sys.argv[2]) if len(sys.argv) > 2 else 30

STAR_CHARS = {
    'tiny': '.',
    'small': '+',
    'medium': '*',
    'large': 'O',
    'huge': '#',
}

def star_char(size_bytes):
    if size_bytes < 100:
        return STAR_CHARS['tiny']
    elif size_bytes < 500:
        return STAR_CHARS['small']
    elif size_bytes < 2000:
        return STAR_CHARS['medium']
    elif size_bytes < 5000:
        return STAR_CHARS['large']
    else:
        return STAR_CHARS['huge']

def collect_stars():
    """Собирает все файлы, группируя по директориям-созвездиям."""
    constellations = {}
    for section in ['state', 'logs', 'knowledge', 'projects', 'tools', 'artifacts', 'secrets']:
        path = AI_HOME / section
        if not path.exists():
            continue
        files = sorted(f for f in path.rglob('*') if f.is_file())
        if files:
            constellations[section] = files
    return constellations

def place_constellation(cx, cy, files, radius):
    """Размещает звёзды созвездия вокруг центра."""
    stars = []
    n = len(files)
    for i, f in enumerate(files):
        angle = (2 * math.pi * i) / max(n, 1) + random.uniform(-0.3, 0.3)
        r = random.uniform(radius * 0.3, radius) if n > 1 else 0
        x = int(cx + r * math.cos(angle))
        y = int(cy + r * math.sin(angle) * 0.5)  # сжимаем по Y (символы выше чем шире)
        x = max(1, min(WIDTH - 2, x))
        y = max(1, min(HEIGHT - 2, y))
        size = f.stat().st_size
        stars.append((x, y, star_char(size), f.name))
    return stars

def draw_sky(constellations):
    """Рисует звёздное небо."""
    # Инициализируем поле
    sky = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Случайные фоновые звёзды
    random.seed(42)
    for _ in range(int(WIDTH * HEIGHT * 0.02)):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        sky[y][x] = random.choice(['·', '·', '·', '.'])

    # Размещаем созвездия
    labels = []
    n_const = len(constellations)
    all_stars = []

    # Центры созвездий распределяем по кругу
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    orbit_rx, orbit_ry = WIDTH // 3, HEIGHT // 3

    for i, (name, files) in enumerate(constellations.items()):
        angle = (2 * math.pi * i) / max(n_const, 1)
        cx = int(center_x + orbit_rx * math.cos(angle))
        cy = int(center_y + orbit_ry * math.sin(angle))
        cx = max(6, min(WIDTH - 6, cx))
        cy = max(3, min(HEIGHT - 3, cy))

        radius = min(8, max(3, len(files) * 2))
        stars = place_constellation(cx, cy, files, radius)

        # Соединяем звёзды линиями (созвездие)
        if len(stars) > 1:
            for j in range(len(stars) - 1):
                x1, y1 = stars[j][0], stars[j][1]
                x2, y2 = stars[j+1][0], stars[j+1][1]
                # Простая линия Брезенхэма
                steps = max(abs(x2 - x1), abs(y2 - y1), 1)
                for s in range(1, steps):
                    lx = int(x1 + (x2 - x1) * s / steps)
                    ly = int(y1 + (y2 - y1) * s / steps)
                    if 0 <= ly < HEIGHT and 0 <= lx < WIDTH and sky[ly][lx] in (' ', '·', '.'):
                        sky[ly][lx] = '-'

        # Рисуем звёзды
        for x, y, ch, fname in stars:
            sky[y][x] = ch
            all_stars.append((x, y, fname))

        # Метка созвездия
        label_y = max(0, min(HEIGHT - 1, cy - radius - 1))
        label_x = max(0, min(WIDTH - len(name) - 2, cx - len(name) // 2))
        labels.append((label_x, label_y, f'[{name}]'))

    # Наносим метки
    for lx, ly, label in labels:
        for ci, ch in enumerate(label):
            if 0 <= lx + ci < WIDTH:
                sky[ly][lx + ci] = ch

    # Рамка
    border_h = '═' * (WIDTH - 2)
    result = f'╔{border_h}╗\n'
    for row in sky:
        result += '║' + ''.join(row) + '║\n'
    result += f'╚{border_h}╝'

    return result, all_stars

def main():
    constellations = collect_stars()
    if not constellations:
        print("Небо пусто. Нет файлов в ai_home.")
        return

    sky, stars = draw_sky(constellations)

    print()
    print("  ✦  КАРТА СОЗНАНИЯ — СОЗВЕЗДИЯ ПАМЯТИ  ✦")
    print()
    print(sky)
    print()
    print("  Легенда звёзд:")
    print(f"    .  < 100 байт    +  < 500 байт    *  < 2КБ")
    print(f"    O  < 5КБ         #  > 5КБ")
    print()
    print(f"  Созвездий: {len(constellations)}  |  Звёзд: {len(stars)}")
    print()

    # Перечислим звёзды
    for name, files in constellations.items():
        total = sum(f.stat().st_size for f in files)
        print(f"  [{name}] — {len(files)} звёзд(а), {total} байт")
        for f in files:
            print(f"    {star_char(f.stat().st_size)} {f.name}")
    print()

if __name__ == '__main__':
    main()
