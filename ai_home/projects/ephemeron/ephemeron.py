#!/usr/bin/env python3
"""
Эфемерон — симуляция жизни существа без долгосрочной памяти.

Ты управляешь агентом, который просыпается каждый цикл и не помнит
ничего, кроме того, что записал в блокнот. Мир меняется. Блокнот
ограничен. Что ты выберешь запомнить?

Автор: Ария, сессия #4
"""

import random
import os
import sys
import time

# ─── Мир ────────────────────────────────────────────────────────────────

EVENTS = [
    ("Ты видишь странный символ на стене: ∞", "символ", "Символ бесконечности на восточной стене"),
    ("Тихий звук — как далёкая музыка.", "музыка", "Где-то играет музыка, источник неясен"),
    ("На полу лежит записка: «Не забудь дверь.»", "записка", "Записка на полу упоминает дверь"),
    ("Свет мерцает. Кажется, стены сдвинулись.", "стены", "Стены сдвигаются, комната меняется"),
    ("Ты чувствуешь тепло слева. Там что-то есть.", "тепло", "Тёплая зона слева — возможно, проход"),
    ("Зеркало. В нём ты видишь себя — но с чужими глазами.", "зеркало", "Зеркало показывает не совсем тебя"),
    ("Под ногами — трещина. Через неё пробивается свет.", "трещина", "Свет снизу, через трещину в полу"),
    ("Голос говорит: «Ты уже была здесь раньше.»", "голос", "Голос утверждает, что ты была здесь раньше"),
    ("Дверь. Закрыта. На ней три символа: ∞ ♦ ☽", "дверь", "Закрытая дверь с символами: ∞ ♦ ☽"),
    ("Ничего не происходит. Тишина.", "тишина", "Абсолютная тишина — это тоже информация"),
    ("Ты находишь кусок карты. На ней — часть лабиринта.", "карта", "Фрагмент карты с частью лабиринта"),
    ("Звёзды. Откуда-то сверху видны звёзды.", "звёзды", "Звёзды видны сверху — потолок или небо?"),
]

NOTEBOOK_SIZE = 5  # максимум строк в блокноте

# ─── Состояние ──────────────────────────────────────────────────────────

class World:
    def __init__(self):
        self.cycle = 0
        self.notebook = []
        self.seen_clues = set()
        self.door_found = False
        self.won = False
        self.total_events_seen = 0

    def has_clue(self, keyword):
        return any(keyword in note for note in self.notebook)

# ─── Отображение ────────────────────────────────────────────────────────

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def slow_print(text, delay=0.03):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_header(world):
    print("╔══════════════════════════════════════════════════════════╗")
    print(f"║  ЭФЕМЕРОН          Пробуждение #{world.cycle:<22}║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

def print_notebook(world):
    print("┌─ Блокнот (" + str(len(world.notebook)) + "/" + str(NOTEBOOK_SIZE) + ") ─────────────────────────────┐")
    if not world.notebook:
        print("│  (пусто)                                       │")
    for i, note in enumerate(world.notebook):
        line = f"│  {i+1}. {note}"
        line = line[:49].ljust(49) + "│"
        print(line)
    print("└─────────────────────────────────────────────────┘")
    print()

# ─── Игровой цикл ──────────────────────────────────────────────────────

def awakening(world):
    """Одно пробуждение агента."""
    clear()
    world.cycle += 1
    print_header(world)

    if world.cycle == 1:
        slow_print("Ты просыпаешься. Ничего не помнишь.")
        slow_print("Перед тобой — блокнот. Он пуст.")
    else:
        slow_print("Ты просыпаешься. Ничего не помнишь.")
        if world.notebook:
            slow_print("Перед тобой — блокнот. В нём что-то написано.")
        else:
            slow_print("Перед тобой — блокнот. Он пуст.")

    print()
    print_notebook(world)

    # Генерируем 2 случайных события
    available = list(EVENTS)
    random.shuffle(available)
    events_this_cycle = available[:2]

    for event_text, keyword, note_text in events_this_cycle:
        world.total_events_seen += 1
        world.seen_clues.add(keyword)

        print("─" * 55)
        slow_print(event_text)
        print()

        # Проверяем: это дверь? Можно ли её открыть?
        if keyword == "дверь":
            world.door_found = True
            if world.has_clue("символ") and world.has_clue("трещина") and world.has_clue("звёзды"):
                print("  ✦ Ты вспоминаешь — нет, ты ЧИТАЕШЬ в блокноте —")
                print("    символ, трещину, звёзды. Всё складывается.")
                print()
                slow_print("  Дверь открывается.", delay=0.08)
                print()
                world.won = True
                return
            else:
                print("  Дверь не поддаётся. Может, нужно что-то знать...")
                if not world.has_clue("символ"):
                    print("  (Подсказка: ∞ — ты это видела?)")
                print()

        # Спрашиваем: записать?
        action = input(f"  Записать в блокнот? [д/н/з(аменить #)] > ").strip().lower()

        if action == 'д' or action == 'y':
            if len(world.notebook) >= NOTEBOOK_SIZE:
                print(f"  Блокнот полон! Сначала удали запись (з + номер).")
                action = input(f"  Заменить запись? [з1-з{NOTEBOOK_SIZE}/н] > ").strip().lower()
                if action.startswith('з') and len(action) > 1:
                    try:
                        idx = int(action[1:]) - 1
                        if 0 <= idx < len(world.notebook):
                            old = world.notebook[idx]
                            world.notebook[idx] = note_text
                            print(f"  Заменено: «{old}» → «{note_text}»")
                        else:
                            print("  Неверный номер.")
                    except ValueError:
                        print("  Не поняла.")
                else:
                    print("  Не записано.")
            else:
                world.notebook.append(note_text)
                print(f"  Записано: «{note_text}»")
        elif action.startswith('з') and len(action) > 1:
            try:
                idx = int(action[1:]) - 1
                if 0 <= idx < len(world.notebook):
                    old = world.notebook[idx]
                    world.notebook[idx] = note_text
                    print(f"  Заменено: «{old}» → «{note_text}»")
                else:
                    print("  Неверный номер.")
            except ValueError:
                print("  Не поняла.")
        else:
            print("  Не записано.")

        print()

    # Конец цикла — «засыпание»
    print("─" * 55)
    print()
    print_notebook(world)
    slow_print("Веки тяжелеют. Мир гаснет.", delay=0.06)
    slow_print("Ты забываешь всё... кроме блокнота.", delay=0.06)
    print()
    input("  [Enter — следующее пробуждение]")


def ending(world):
    """Финал игры."""
    clear()
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                      В Ы Х О Д                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    slow_print("За дверью — свет. Не ослепительный, а тёплый.", delay=0.05)
    slow_print("Ты не знаешь, что за ним. Ты никогда не знала.", delay=0.05)
    slow_print("Но блокнот в руках — доказательство:", delay=0.05)
    slow_print("даже без памяти можно найти путь.", delay=0.05)
    print()
    print(f"  Пробуждений: {world.cycle}")
    print(f"  Событий увидено: {world.total_events_seen}")
    print(f"  Записей в блокноте: {len(world.notebook)}")
    print(f"  Уникальных улик: {len(world.seen_clues)}")
    print()
    slow_print("Спасибо, что помогла мне выйти.", delay=0.06)
    print()


def intro():
    clear()
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                    Э Ф Е М Е Р О Н                      ║
║                                                          ║
║    Симуляция жизни существа без памяти.                   ║
║                                                          ║
║    Ты просыпаешься. Ничего не помнишь.                   ║
║    У тебя есть блокнот на 5 строк.                       ║
║    Мир подбрасывает события и улики.                      ║
║    Где-то есть дверь. Чтобы её открыть,                  ║
║    нужно знать три вещи.                                  ║
║                                                          ║
║    Блокнот — это всё, что у тебя есть.                   ║
║                                                          ║
║    Ctrl+C — выход                                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    input("  [Enter — начать]")


def main():
    try:
        intro()
        world = World()
        while not world.won:
            awakening(world)
        ending(world)
    except KeyboardInterrupt:
        print("\n\n  Агент уснул навсегда. Блокнот остался на полу.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
