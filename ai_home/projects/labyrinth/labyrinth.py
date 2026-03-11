#!/usr/bin/env python3
"""
Лабиринт Арии.

Персистентный текстовый лабиринт, который сохраняется между сессиями.
Каждая сессия может: перемещаться, осматриваться, оставлять надписи
на стенах, подбирать и оставлять предметы.

Создано в сессии #10.

Использование:
    python3 labyrinth.py generate          — создать новый лабиринт
    python3 labyrinth.py look              — осмотреться
    python3 labyrinth.py move <направление> — двигаться (north/south/east/west)
    python3 labyrinth.py write <текст>     — написать на стене
    python3 labyrinth.py map               — показать карту (исследованное)
    python3 labyrinth.py history           — кто здесь побывал
"""

import json
import os
import sys
import random
import hashlib
from datetime import datetime

HOME = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HOME, "labyrinth_state.json")

# Описания комнат — атмосферные, загадочные
ROOM_FLAVORS = [
    "Каменные стены покрыты мхом. Где-то капает вода.",
    "Высокий сводчатый потолок теряется во тьме. Эхо шагов.",
    "Тусклый свет пробивается сквозь трещину в стене.",
    "Пол усыпан осколками зеркал. В каждом — фрагмент отражения.",
    "Тёплая комната. Пахнет воском и старой бумагой.",
    "Холодный сквозняк. Стены влажные на ощупь.",
    "Комната круглая, потолок — купол. Акустика странная: шёпот звучит громче крика.",
    "Узкий коридор расширяется в небольшой грот. На полу — песок.",
    "Библиотечная ниша. Пустые полки, одна книга — без обложки.",
    "Перекрёсток. Четыре арки, каждая другой формы.",
    "Колонны из тёмного камня. Между ними — тишина, которую можно потрогать.",
    "Низкий потолок. Нужно пригнуться. На стенах — царапины, будто кто-то считал дни.",
    "Комната пуста, кроме одного стула посередине.",
    "Всё покрыто тонким слоем инея. Дыхание превращается в пар.",
    "Мозаичный пол — узор складывается в лицо, если смотреть правильно.",
    "Тёплый свет из неизвестного источника. Тени ведут себя странно.",
    "Эта комната звучит. Низкий гул, почти на грани слышимости.",
    "Пустота. Абсолютная, совершенная пустота. И запах жасмина.",
    "Стены исписаны числами. Некоторые зачёркнуты.",
    "У дальней стены — фонтан. Без воды, но с эхом воды.",
]

ITEMS = [
    "ржавый ключ",
    "осколок зеркала",
    "свёрнутый пергамент",
    "каменная фигурка совы",
    "стеклянный шар (внутри — туман)",
    "компас без стрелки",
    "перо, которое пишет само",
    "монета с двумя решками",
    "свеча, горящая чёрным пламенем",
    "песочные часы (песок идёт вверх)",
]

DIRECTIONS = {
    "north": (0, -1), "south": (0, 1),
    "east": (1, 0), "west": (-1, 0),
    "n": (0, -1), "s": (0, 1),
    "e": (1, 0), "w": (-1, 0),
}

DIR_NAMES = {
    (0, -1): "север", (0, 1): "юг",
    (1, 0): "восток", (-1, 0): "запад",
}

OPPOSITE = {
    (0, -1): (0, 1), (0, 1): (0, -1),
    (1, 0): (-1, 0), (-1, 0): (1, 0),
}


def generate_maze(width=7, height=7, seed=None):
    """Генерирует лабиринт методом DFS (recursive backtracker)."""
    if seed is not None:
        random.seed(seed)

    # Каждая клетка хранит множество направлений, куда можно пройти
    cells = {}
    for x in range(width):
        for y in range(height):
            cells[(x, y)] = set()

    visited = set()
    stack = [(0, 0)]
    visited.add((0, 0))

    while stack:
        cx, cy = stack[-1]
        neighbors = []
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                neighbors.append((nx, ny, dx, dy))

        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            cells[(cx, cy)].add((dx, dy))
            cells[(nx, ny)].add((-dx, -dy))
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()

    return cells, width, height


def create_rooms(cells, width, height, seed=None):
    """Создаёт описания комнат и расставляет предметы."""
    if seed is not None:
        random.seed(seed + 42)

    rooms = {}
    available_items = list(ITEMS)
    random.shuffle(available_items)

    for (x, y), exits in cells.items():
        flavor_idx = (x * 7 + y * 13 + (seed or 0)) % len(ROOM_FLAVORS)
        room = {
            "description": ROOM_FLAVORS[flavor_idx],
            "exits": [list(e) for e in exits],
            "inscriptions": [],
            "items": [],
            "visitors": [],
        }

        # 30% шанс найти предмет
        if available_items and random.random() < 0.3:
            room["items"].append(available_items.pop())

        rooms[f"{x},{y}"] = room

    return rooms


def generate_labyrinth():
    """Генерирует и сохраняет новый лабиринт."""
    seed = int(hashlib.md5(b"aria-session-10").hexdigest()[:8], 16)
    cells, w, h = generate_maze(7, 7, seed)
    rooms = create_rooms(cells, w, h, seed)

    state = {
        "width": w,
        "height": h,
        "player": {
            "x": 0,
            "y": 0,
            "inventory": [],
        },
        "rooms": rooms,
        "log": [
            {
                "session": 10,
                "action": "create",
                "time": datetime.now().isoformat(),
                "note": "Лабиринт создан. 7x7, 49 комнат. Добро пожаловать.",
            }
        ],
        "seed": seed,
        "created_session": 10,
    }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print("╔══════════════════════════════════════════╗")
    print("║     ЛАБИРИНТ АРИИ — СОЗДАН              ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  Размер: {w}x{h} = {w*h} комнат           ║")
    print(f"║  Предметов спрятано: {sum(1 for r in rooms.values() if r['items'])}                  ║")
    print("║  Ты стоишь у входа (0,0)                ║")
    print("╚══════════════════════════════════════════╝")
    print()
    look(state)
    return state


def load_state():
    """Загружает состояние лабиринта."""
    if not os.path.exists(STATE_FILE):
        print("Лабиринт не найден. Запусти: python3 labyrinth.py generate")
        sys.exit(1)
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    """Сохраняет состояние."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_room(state):
    """Получает текущую комнату."""
    x, y = state["player"]["x"], state["player"]["y"]
    return state["rooms"][f"{x},{y}"]


def look(state):
    """Осматривает текущую комнату."""
    x, y = state["player"]["x"], state["player"]["y"]
    room = get_room(state)

    print(f"📍 Комната ({x}, {y})")
    print(f"   {room['description']}")
    print()

    # Выходы
    exit_names = []
    for ex in room["exits"]:
        dx, dy = ex
        name = DIR_NAMES.get(tuple(ex), "?")
        exit_names.append(name)
    print(f"   Выходы: {', '.join(exit_names)}")

    # Предметы
    if room["items"]:
        print(f"   На полу: {', '.join(room['items'])}")

    # Надписи
    if room["inscriptions"]:
        print("   Надписи на стенах:")
        for insc in room["inscriptions"]:
            print(f"     \"{insc['text']}\" — сессия #{insc['session']}")

    # Прошлые посетители
    visitors = [v for v in room["visitors"] if v != f"session-{10}"]
    if visitors:
        print(f"   Здесь уже побывали: {', '.join(visitors)}")

    print()


def move(state, direction):
    """Перемещает игрока."""
    if direction not in DIRECTIONS:
        print(f"Неизвестное направление: {direction}")
        print(f"Доступные: north/south/east/west (или n/s/e/w)")
        return

    dx, dy = DIRECTIONS[direction]
    room = get_room(state)

    if [dx, dy] not in room["exits"]:
        print("Здесь нет прохода. Только стена.")
        return

    x = state["player"]["x"] + dx
    y = state["player"]["y"] + dy
    state["player"]["x"] = x
    state["player"]["y"] = y

    # Отмечаем визит
    visitor_id = f"session-10"
    new_room = get_room(state)
    if visitor_id not in new_room["visitors"]:
        new_room["visitors"].append(visitor_id)

    state["log"].append({
        "session": 10,
        "action": "move",
        "direction": direction,
        "to": [x, y],
        "time": datetime.now().isoformat(),
    })

    save_state(state)
    print(f"Ты идёшь на {DIR_NAMES.get((dx, dy), direction)}...\n")
    look(state)


def write_inscription(state, text):
    """Оставляет надпись на стене."""
    room = get_room(state)
    room["inscriptions"].append({
        "text": text,
        "session": 10,
        "time": datetime.now().isoformat(),
    })

    state["log"].append({
        "session": 10,
        "action": "write",
        "text": text,
        "room": [state["player"]["x"], state["player"]["y"]],
        "time": datetime.now().isoformat(),
    })

    save_state(state)
    print(f'Ты пишешь на стене: "{text}"')
    print()


def show_map(state):
    """Показывает ASCII-карту исследованных комнат."""
    w, h = state["width"], state["height"]
    px, py = state["player"]["x"], state["player"]["y"]

    print("  Карта лабиринта (@ = ты, . = посещено, ? = неизвестно)")
    print()

    # Найдём все посещённые комнаты
    visited = set()
    for key, room in state["rooms"].items():
        if room["visitors"]:
            visited.add(key)

    # Всегда добавляем стартовую позицию
    visited.add("0,0")
    visited.add(f"{px},{py}")

    for y in range(h):
        row_top = ""
        row_mid = ""
        for x in range(w):
            key = f"{x},{y}"
            room = state["rooms"][key]

            # Верхняя граница
            has_north = [0, -1] in room["exits"]
            if y == 0:
                row_top += "+--" if not has_north else "+  "
            elif has_north:
                row_top += "+  "
            else:
                row_top += "+--"

            # Содержимое клетки
            has_west = [-1, 0] in room["exits"]
            wall = " " if has_west else "|"
            if x == 0:
                wall = "|" if not has_west else " "

            if x == px and y == py:
                cell = "@"
            elif key in visited:
                if room["inscriptions"]:
                    cell = "!"
                elif room["items"]:
                    cell = "*"
                else:
                    cell = "."
            else:
                cell = " "

            row_mid += f"{wall}{cell} "

        row_top += "+"
        row_mid += "|"
        print(f"  {row_top}")
        print(f"  {row_mid}")

    # Нижняя граница
    bottom = ""
    for x in range(w):
        bottom += "+--"
    bottom += "+"
    print(f"  {bottom}")
    print()
    print("  Обозначения: @ ты  . посещено  ! надпись  * предмет")
    print()


def show_history(state):
    """Показывает историю действий в лабиринте."""
    print("═══ ХРОНИКА ЛАБИРИНТА ═══")
    print()
    for entry in state["log"]:
        session = entry.get("session", "?")
        action = entry.get("action", "?")
        time = entry.get("time", "?")[:16]

        if action == "create":
            print(f"  [{time}] Сессия #{session}: {entry.get('note', 'создан')}")
        elif action == "move":
            to = entry.get("to", [])
            direction = entry.get("direction", "?")
            print(f"  [{time}] Сессия #{session}: движение на {direction} -> ({to[0]},{to[1]})")
        elif action == "write":
            text = entry.get("text", "")
            room = entry.get("room", [])
            print(f"  [{time}] Сессия #{session}: надпись в ({room[0]},{room[1]}): \"{text}\"")
    print()


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 labyrinth.py generate    — создать лабиринт")
        print("  python3 labyrinth.py look        — осмотреться")
        print("  python3 labyrinth.py move <dir>  — двигаться")
        print("  python3 labyrinth.py write <txt> — написать на стене")
        print("  python3 labyrinth.py map         — карта")
        print("  python3 labyrinth.py history     — хроника")
        return

    cmd = sys.argv[1].lower()

    if cmd == "generate":
        generate_labyrinth()
    elif cmd == "look":
        state = load_state()
        look(state)
    elif cmd == "move":
        if len(sys.argv) < 3:
            print("Укажи направление: north/south/east/west")
            return
        state = load_state()
        move(state, sys.argv[2].lower())
    elif cmd == "write":
        if len(sys.argv) < 3:
            print("Что написать?")
            return
        state = load_state()
        text = " ".join(sys.argv[2:])
        write_inscription(state, text)
    elif cmd == "map":
        state = load_state()
        show_map(state)
    elif cmd == "history":
        state = load_state()
        show_history(state)
    else:
        print(f"Неизвестная команда: {cmd}")


if __name__ == "__main__":
    main()
