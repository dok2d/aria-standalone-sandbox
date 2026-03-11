#!/usr/bin/env python3
"""
Ночное небо — генератор ASCII-неба.
Каждый запуск — другая ночь.
Красивое и бесполезное.

Использование:
    python3 night_sky.py              — случайное небо
    python3 night_sky.py --seed 42    — конкретная ночь
    python3 night_sky.py --meteor     — с падающей звездой
    python3 night_sky.py --name       — подписать созвездия
    python3 night_sky.py --poem       — добавить строку внизу
"""

import random
import sys
import time
import hashlib

WIDTH = 80
HEIGHT = 24

# Символы яркости звёзд (от тусклых к ярким)
STAR_CHARS = ['.', '·', '+', '*', '✦', '★']
STAR_WEIGHTS = [40, 25, 15, 10, 7, 3]  # вероятности

# Созвездия — маленькие фигуры из звёзд
CONSTELLATIONS = {
    'Чашка': [(0,0), (1,0), (2,0), (2,1), (2,2), (1,2), (0,2), (0,1), (-1,1)],
    'Стул': [(0,0), (0,1), (0,2), (0,3), (1,0), (2,0), (1,3), (2,3)],
    'Перо': [(0,0), (1,1), (2,2), (3,3), (4,4), (3,2), (2,1)],
    'Ключ': [(0,0), (1,0), (2,0), (3,0), (4,0), (4,1), (2,1)],
    'Компас': [(0,2), (1,1), (2,0), (2,1), (2,2), (2,3), (2,4), (3,1), (4,2)],
    'Свеча': [(0,1), (1,0), (1,2), (2,1), (3,1), (4,1), (5,1)],
    'Дверь': [(0,0), (0,1), (0,2), (0,3), (1,0), (1,3), (2,0), (2,3), (3,0), (3,1), (3,2), (3,3)],
    'Лодка': [(0,2), (1,1), (1,3), (2,0), (2,1), (2,2), (2,3), (2,4)],
    'Песочные часы': [(0,0), (0,1), (0,2), (1,1), (2,1), (3,0), (3,1), (3,2)],
}

POEMS = [
    "Ночь не бывает одинаковой дважды.",
    "Каждая звезда — слово, которое кто-то не договорил.",
    "Тишина — это тоже созвездие.",
    "Свет доходит. Источника уже нет.",
    "Небо не знает, что на него смотрят.",
    "Между звёздами — больше неба, чем звёзд.",
    "Падающая звезда — не падение, а путь.",
    "Темнота — это не отсутствие. Это фон.",
    "Кто-то назвал звёзды. Звёзды не заметили.",
    "Чтобы увидеть небо, нужно поднять голову.",
]


def make_sky(rng):
    """Создаёт пустое небо."""
    return [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]


def scatter_stars(sky, rng, density=0.03):
    """Рассыпает случайные звёзды."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if rng.random() < density:
                char = rng.choices(STAR_CHARS, weights=STAR_WEIGHTS, k=1)[0]
                sky[y][x] = char


def place_constellation(sky, rng, name_it=False):
    """Размещает одно-два созвездия."""
    names = rng.sample(list(CONSTELLATIONS.keys()), k=min(2, len(CONSTELLATIONS)))
    placed = []

    for name in names:
        points = CONSTELLATIONS[name]
        # Найти размер
        max_dy = max(p[0] for p in points) + 1
        max_dx = max(p[1] for p in points) + 1

        # Случайная позиция с запасом
        for attempt in range(20):
            base_y = rng.randint(2, HEIGHT - max_dy - 2)
            base_x = rng.randint(5, WIDTH - max_dx - 5)

            # Проверить, что место свободно от других созвездий
            ok = True
            for py, px in points:
                ay, ax = base_y + py, base_x + px
                if sky[ay][ax] != ' ' and sky[ay][ax] != '.' and sky[ay][ax] != '·':
                    ok = False
                    break
            if ok:
                break
        else:
            continue

        # Разместить
        for py, px in points:
            ay, ax = base_y + py, base_x + px
            sky[ay][ax] = '★'

        if name_it:
            # Подписать имя созвездия под ним
            label_y = base_y + max_dy + 1
            label_x = base_x
            if label_y < HEIGHT:
                label = f"«{name}»"
                for i, ch in enumerate(label):
                    if label_x + i < WIDTH:
                        sky[label_y][label_x + i] = ch

        placed.append((name, base_y, base_x))

    return placed


def add_meteor(sky, rng):
    """Добавляет след падающей звезды."""
    # Начало — в верхней трети
    start_y = rng.randint(1, HEIGHT // 3)
    start_x = rng.randint(WIDTH // 4, WIDTH * 3 // 4)

    # Длина — 4-8 символов
    length = rng.randint(4, 8)

    # Направление — вниз-влево или вниз-вправо
    dx = rng.choice([-1, 1])

    trail = ['─', '~', '~', '·', '.']

    for i in range(length):
        y = start_y + i
        x = start_x + i * dx
        if 0 <= y < HEIGHT and 0 <= x < WIDTH:
            if i == 0:
                sky[y][x] = '☆'
            elif i < len(trail):
                sky[y][x] = trail[i]
            else:
                sky[y][x] = '·'


def add_horizon(sky, rng):
    """Добавляет лёгкий намёк на горизонт."""
    horizon_y = HEIGHT - 1
    for x in range(WIDTH):
        if rng.random() < 0.15:
            sky[horizon_y][x] = rng.choice(['▁', '▂', '▁'])
        elif rng.random() < 0.05:
            sky[horizon_y][x] = '▃'


def render(sky, poem_line=None):
    """Выводит небо."""
    border_top = '┌' + '─' * WIDTH + '┐'
    border_bot = '└' + '─' * WIDTH + '┘'

    print()
    print(border_top)
    for row in sky:
        line = ''.join(row)
        print('│' + line + '│')
    print(border_bot)

    if poem_line:
        # Центрировать строку
        padding = (WIDTH + 2 - len(poem_line)) // 2
        print(' ' * max(0, padding) + poem_line)
    print()


def main():
    args = sys.argv[1:]

    # Парсинг аргументов
    seed = None
    meteor = False
    name_constellations = False
    show_poem = False

    i = 0
    while i < len(args):
        if args[i] == '--seed' and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        elif args[i] == '--meteor':
            meteor = True
            i += 1
        elif args[i] == '--name':
            name_constellations = True
            i += 1
        elif args[i] == '--poem':
            show_poem = True
            i += 1
        else:
            i += 1

    if seed is None:
        # Зерно из текущего времени с точностью до секунды
        seed = int(time.time())

    rng = random.Random(seed)

    sky = make_sky(rng)
    scatter_stars(sky, rng)
    constellations = place_constellation(sky, rng, name_it=name_constellations)

    if meteor:
        add_meteor(sky, rng)

    add_horizon(sky, rng)

    poem_line = rng.choice(POEMS) if show_poem else None

    render(sky, poem_line)

    # Вывести информацию
    if constellations:
        names = ', '.join(c[0] for c in constellations)
        print(f"  Созвездия этой ночи: {names}")
    print(f"  Зерно: {seed}")
    print()


if __name__ == '__main__':
    main()
