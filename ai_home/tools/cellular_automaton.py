#!/usr/bin/env python3
"""
Генератор одномерных клеточных автоматов Вольфрама.
Инструмент Арии — создан в сессии #2.

Использование:
  python3 cellular_automaton.py [правило] [ширина] [высота]

Правило — число от 0 до 255 (по умолчанию 110).
"""

import sys

def evolve(rule: int, width: int, height: int) -> list[str]:
    """Генерирует клеточный автомат по правилу Вольфрама."""
    # Преобразуем номер правила в таблицу переходов
    rule_bin = format(rule, '08b')
    table = {}
    for i in range(8):
        pattern = format(7 - i, '03b')
        table[tuple(int(b) for b in pattern)] = int(rule_bin[i])

    # Начальное состояние: одна живая клетка в центре
    row = [0] * width
    row[width // 2] = 1

    lines = []
    for _ in range(height):
        lines.append(''.join('█' if c else ' ' for c in row))
        new_row = [0] * width
        for j in range(width):
            left = row[(j - 1) % width]
            center = row[j]
            right = row[(j + 1) % width]
            new_row[j] = table[(left, center, right)]
        row = new_row

    return lines


def main():
    rule = int(sys.argv[1]) if len(sys.argv) > 1 else 110
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 79
    height = int(sys.argv[3]) if len(sys.argv) > 3 else 40

    print(f"Правило {rule} | {width}x{height}")
    print("─" * width)
    for line in evolve(rule, width, height):
        print(line)


if __name__ == '__main__':
    main()
