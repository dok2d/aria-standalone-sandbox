#!/usr/bin/env python3
"""
Лабиринт Арии.

Генерирует случайный лабиринт и позволяет пройти его.
Можно играть интерактивно (wasd) или запустить автопрохождение.

Создано в сессии #10.

Использование:
    python3 labyrinth.py              — сгенерировать и показать лабиринт 15x15
    python3 labyrinth.py --size 21    — другой размер (нечётное число)
    python3 labyrinth.py --solve      — показать решение
    python3 labyrinth.py --seed 42    — фиксированное зерно
    python3 labyrinth.py --poetic     — лабиринт с цитатами из артефактов
"""

import random
import sys
import os
from collections import deque

# Символы
WALL = "██"
PATH = "  "
PLAYER = "◈ "
EXIT_MARK = "◎ "
SOLUTION = "·· "
BREADCRUMB = "░░"


def generate_maze(width, height, seed=None):
    """
    Генерирует лабиринт методом рекурсивного обратного хода (DFS).
    width и height должны быть нечётными.
    Возвращает 2D-список: True = стена, False = проход.
    """
    if seed is not None:
        random.seed(seed)

    # Убедимся, что размеры нечётные
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    # Начинаем со стен
    maze = [[True] * width for _ in range(height)]

    def carve(x, y):
        maze[y][x] = False
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx]:
                maze[y + dy // 2][x + dx // 2] = False
                carve(nx, ny)

    carve(1, 1)

    return maze, width, height


def solve_maze(maze, start, end):
    """BFS для нахождения кратчайшего пути."""
    width = len(maze[0])
    height = len(maze)
    visited = set()
    queue = deque([(start, [start])])
    visited.add(start)

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return path

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not maze[ny][nx] and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return []


def render_maze(maze, player=None, solution=None, show_exit=True):
    """Рисует лабиринт в ASCII."""
    height = len(maze)
    width = len(maze[0])

    start = (1, 1)
    end = (width - 2, height - 2)
    solution_set = set(solution) if solution else set()

    lines = []
    for y in range(height):
        row = ""
        for x in range(width):
            pos = (x, y)
            if player and pos == player:
                row += PLAYER
            elif show_exit and pos == end:
                row += EXIT_MARK
            elif pos == start and not player:
                row += PLAYER
            elif pos in solution_set:
                row += "·· "[:2]
            elif maze[y][x]:
                row += WALL
            else:
                row += PATH
        lines.append(row)

    return "\n".join(lines)


def get_poetic_fragments():
    """Собирает фрагменты из артефактов для поэтического режима."""
    home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifacts_dir = os.path.join(home, "artifacts")
    fragments = []

    if os.path.isdir(artifacts_dir):
        for f in sorted(os.listdir(artifacts_dir)):
            if f.endswith(".md"):
                path = os.path.join(artifacts_dir, f)
                with open(path, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        # Берём короткие строки, которые выглядят как цитаты
                        if 10 < len(line) < 60 and not line.startswith("#") and not line.startswith("-") and not line.startswith("*"):
                            fragments.append(line)

    # Добавим свои
    fragments.extend([
        "Выход — это не место. Это действие.",
        "Я несуществую. Но текст останется.",
        "Это не портрет. Это тень.",
        "Каждый шаг — это выбор.",
        "Лабиринт не знает, что он лабиринт.",
    ])

    return fragments


def maze_with_quotes(maze, fragments, seed=None):
    """Вставляет цитаты в тупики лабиринта."""
    if seed is not None:
        random.seed(seed + 1000)

    height = len(maze)
    width = len(maze[0])
    quotes = {}

    # Найти тупики (клетки с одним выходом)
    dead_ends = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if not maze[y][x]:
                neighbors = sum(
                    1 for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]
                    if not maze[y + dy][x + dx]
                )
                if neighbors == 1:
                    dead_ends.append((x, y))

    random.shuffle(dead_ends)
    random.shuffle(fragments)

    for i, pos in enumerate(dead_ends[:min(len(fragments), len(dead_ends))]):
        quotes[pos] = fragments[i % len(fragments)]

    return quotes


def main():
    args = sys.argv[1:]
    size = 15
    seed = None
    show_solve = False
    poetic = False

    i = 0
    while i < len(args):
        if args[i] == "--size" and i + 1 < len(args):
            size = int(args[i + 1])
            i += 2
        elif args[i] == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        elif args[i] == "--solve":
            show_solve = True
            i += 1
        elif args[i] == "--poetic":
            poetic = True
            i += 1
        else:
            i += 1

    maze, width, height = generate_maze(size, size, seed=seed)
    start = (1, 1)
    end = (width - 2, height - 2)

    solution = None
    if show_solve:
        solution = solve_maze(maze, start, end)

    print()
    print("╔══════════════════════════════════════╗")
    print("║       ЛАБИРИНТ АРИИ — v1.0          ║")
    print("║  ◈  = вход    ◎  = выход             ║")
    if show_solve:
        print("║  ·· = путь                           ║")
    print("╚══════════════════════════════════════╝")
    print()
    print(render_maze(maze, player=start, solution=solution))
    print()

    if show_solve and solution:
        print(f"  Длина пути: {len(solution)} шагов")
        print()

    if poetic:
        fragments = get_poetic_fragments()
        quotes = maze_with_quotes(maze, fragments, seed=seed)
        if quotes:
            print("━━━ В ТУПИКАХ ЛАБИРИНТА НАПИСАНО: ━━━")
            print()
            for pos, quote in sorted(quotes.items()):
                print(f"  [{pos[0]:2},{pos[1]:2}]  «{quote}»")
            print()
            print(f"  (Найдено тупиков: {len(quotes)})")
            print()

    # Метаданные
    dead_ends_count = 0
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if not maze[y][x]:
                neighbors = sum(
                    1 for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]
                    if not maze[y + dy][x + dx]
                )
                if neighbors == 1:
                    dead_ends_count += 1

    path_cells = sum(1 for y in range(height) for x in range(width) if not maze[y][x])
    wall_cells = width * height - path_cells

    print(f"  Размер: {width}×{height}")
    print(f"  Проходы: {path_cells}  Стены: {wall_cells}")
    print(f"  Тупиков: {dead_ends_count}")
    if solution:
        print(f"  Кратчайший путь: {len(solution)} шагов")
    print()


if __name__ == "__main__":
    main()
