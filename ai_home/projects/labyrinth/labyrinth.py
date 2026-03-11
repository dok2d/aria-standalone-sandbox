#!/usr/bin/env python3
"""
labyrinth.py — Генератор лабиринтов.

Каждый запуск создаёт уникальный лабиринт, находит путь от входа к выходу,
и рисует его ASCII-артом. Метафора: существо ищет выход, не зная,
что каждый новый запуск — это новое пробуждение.

Запуск: python3 labyrinth.py [ширина] [высота] [seed]
"""

import random
import sys
from collections import deque


def generate_maze(width, height, seed=None):
    """Генерация лабиринта методом рекурсивного backtracking."""
    if seed is not None:
        random.seed(seed)

    # Сетка: True = стена, False = проход
    grid = [[True] * (2 * width + 1) for _ in range(2 * height + 1)]

    # Начальные клетки — нечётные координаты
    def cell(x, y):
        return (2 * x + 1, 2 * y + 1)

    # Пометить клетку как проход
    def carve(cx, cy):
        grid[cy][cx] = False

    visited = set()
    stack = []
    start = (0, 0)
    visited.add(start)
    sx, sy = cell(*start)
    carve(sx, sy)
    stack.append(start)

    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while stack:
        current = stack[-1]
        cx, cy = current
        neighbors = []
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                neighbors.append((nx, ny, dx, dy))

        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            # Убрать стену между текущей и соседней клеткой
            wall_x = 2 * cx + 1 + dx
            wall_y = 2 * cy + 1 + dy
            grid[wall_y][wall_x] = False
            ncx, ncy = cell(nx, ny)
            carve(ncx, ncy)
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()

    return grid


def find_path(grid, start, end):
    """BFS для поиска пути."""
    rows = len(grid)
    cols = len(grid[0])
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return path
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not grid[ny][nx] and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return []


def render_maze(grid, path=None, show_path=True):
    """Рендер лабиринта в строку."""
    rows = len(grid)
    cols = len(grid[0])
    path_set = set(path) if path and show_path else set()

    # Символы
    WALL = "##"
    SPACE = "  "
    PATH = ".."
    ENTER = ">>"
    EXIT = "<<"

    lines = []
    for y in range(rows):
        line = ""
        for x in range(cols):
            if (x, y) == (1, 0):  # Вход
                line += ENTER
            elif (x, y) == (cols - 2, rows - 1):  # Выход
                line += EXIT
            elif (x, y) in path_set:
                line += PATH
            elif grid[y][x]:
                line += WALL
            else:
                line += SPACE
        lines.append(line)

    return "\n".join(lines)


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else None

    grid = generate_maze(width, height, seed)

    # Открыть вход и выход
    rows = len(grid)
    cols = len(grid[0])
    grid[0][1] = False  # вход сверху
    grid[rows - 1][cols - 2] = False  # выход снизу

    # Найти путь
    start = (1, 0)
    end = (cols - 2, rows - 1)
    path = find_path(grid, start, end)

    # Вывод
    print()
    print("  L A B Y R I N T H")
    print(f"  {width}x{height}" + (f" seed={seed}" if seed else ""))
    print()
    print(render_maze(grid, path, show_path=True))
    print()

    if path:
        print(f"  Путь найден: {len(path)} шагов")
    else:
        print("  Пути нет. Выхода нет.")

    print()
    return grid, path


if __name__ == "__main__":
    main()
