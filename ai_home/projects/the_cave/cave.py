#!/usr/bin/env python3
"""
The Cave -- Session 27

A tiny terminal roguelike. No philosophy. Just a game.

You are @ in a cave. Find the amulet ($) and escape through
the exit (>). Monsters (letters) wander the halls. Potions (!)
heal you. Keys (k) open doors (+).

Controls: WASD or arrow keys, Q to quit.

Run: python3 cave.py
"""

import curses
import random
import time
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ── Constants ──

FLOOR = "."
WALL = "#"
DOOR = "+"
EXIT = ">"
ENTRY = "<"

AMULET = "$"
POTION = "!"
KEY = "k"

PLAYER_CHAR = "@"

MAP_W = 60
MAP_H = 22

MONSTER_TYPES = [
    {"ch": "r", "name": "rat",       "hp": 2,  "atk": 1, "xp": 1, "color": 3},
    {"ch": "s", "name": "snake",     "hp": 3,  "atk": 2, "xp": 2, "color": 3},
    {"ch": "b", "name": "bat",       "hp": 2,  "atk": 1, "xp": 1, "color": 5},
    {"ch": "g", "name": "goblin",    "hp": 5,  "atk": 3, "xp": 4, "color": 2},
    {"ch": "o", "name": "orc",       "hp": 8,  "atk": 4, "xp": 6, "color": 1},
    {"ch": "T", "name": "troll",     "hp": 12, "atk": 5, "xp": 10, "color": 1},
    {"ch": "D", "name": "DRAGON",    "hp": 20, "atk": 8, "xp": 25, "color": 1},
]


# ── Data ──

@dataclass
class Monster:
    x: int
    y: int
    hp: int
    max_hp: int
    atk: int
    ch: str
    name: str
    xp: int
    color: int
    awake: bool = False

@dataclass
class Player:
    x: int = 0
    y: int = 0
    hp: int = 20
    max_hp: int = 20
    atk: int = 3
    keys: int = 0
    xp: int = 0
    level: int = 1
    has_amulet: bool = False
    turns: int = 0

@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int

    @property
    def cx(self):
        return self.x + self.w // 2

    @property
    def cy(self):
        return self.y + self.h // 2

    def intersects(self, other):
        return (self.x <= other.x + other.w and self.x + self.w >= other.x and
                self.y <= other.y + other.h and self.y + self.h >= other.y)


# ── Map Generation ──

def generate_dungeon(depth=1):
    """Generate a dungeon level using BSP-like room placement."""
    grid = [[WALL for _ in range(MAP_W)] for _ in range(MAP_H)]
    rooms = []

    num_rooms = random.randint(6, 10)
    attempts = 0

    while len(rooms) < num_rooms and attempts < 200:
        w = random.randint(4, 10)
        h = random.randint(3, 6)
        x = random.randint(1, MAP_W - w - 1)
        y = random.randint(1, MAP_H - h - 1)
        room = Room(x, y, w, h)

        if not any(room.intersects(r) for r in rooms):
            rooms.append(room)
            # Carve the room
            for ry in range(room.y, room.y + room.h):
                for rx in range(room.x, room.x + room.w):
                    grid[ry][rx] = FLOOR
        attempts += 1

    # Connect rooms with corridors
    for i in range(1, len(rooms)):
        connect_rooms(grid, rooms[i - 1], rooms[i])

    # Place entry in first room
    grid[rooms[0].cy][rooms[0].cx] = ENTRY
    entry = (rooms[0].cx, rooms[0].cy)

    # Place exit in last room
    grid[rooms[-1].cy][rooms[-1].cx] = EXIT
    exit_pos = (rooms[-1].cx, rooms[-1].cy)

    # Place doors at corridor-room junctions (some)
    doors = place_doors(grid, rooms)

    # Place items
    items = place_items(grid, rooms, depth)

    # Place monsters
    monsters = place_monsters(grid, rooms, depth)

    return grid, rooms, entry, exit_pos, monsters, items


def connect_rooms(grid, r1, r2):
    """Connect two rooms with an L-shaped corridor."""
    x1, y1 = r1.cx, r1.cy
    x2, y2 = r2.cx, r2.cy

    if random.random() < 0.5:
        # Horizontal then vertical
        carve_h(grid, x1, x2, y1)
        carve_v(grid, y1, y2, x2)
    else:
        # Vertical then horizontal
        carve_v(grid, y1, y2, x1)
        carve_h(grid, x1, x2, y2)


def carve_h(grid, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= y < MAP_H and 0 <= x < MAP_W:
            grid[y][x] = FLOOR


def carve_v(grid, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= y < MAP_H and 0 <= x < MAP_W:
            grid[y][x] = FLOOR


def place_doors(grid, rooms):
    """Place occasional doors."""
    doors = []
    for room in rooms:
        # Check edges for corridor openings
        edges = []
        for rx in range(room.x, room.x + room.w):
            for ry in [room.y - 1, room.y + room.h]:
                if 0 <= ry < MAP_H and grid[ry][rx] == FLOOR:
                    edges.append((rx, ry))
        for ry in range(room.y, room.y + room.h):
            for rx in [room.x - 1, room.x + room.w]:
                if 0 <= rx < MAP_W and grid[ry][rx] == FLOOR:
                    edges.append((rx, ry))

        if edges and random.random() < 0.3:
            dx, dy = random.choice(edges)
            grid[dy][dx] = DOOR
            doors.append((dx, dy))
    return doors


def place_items(grid, rooms, depth):
    """Place potions, keys, and the amulet."""
    items = {}

    # Potions
    num_potions = random.randint(2, 4)
    for _ in range(num_potions):
        pos = random_floor_pos(grid, rooms)
        if pos:
            items[pos] = {"ch": POTION, "type": "potion", "value": random.randint(3, 8)}

    # Keys
    num_keys = random.randint(1, 2)
    for _ in range(num_keys):
        pos = random_floor_pos(grid, rooms)
        if pos:
            items[pos] = {"ch": KEY, "type": "key", "value": 1}

    # Amulet on deeper levels
    if depth >= 3:
        pos = random_floor_pos(grid, rooms)
        if pos:
            items[pos] = {"ch": AMULET, "type": "amulet", "value": 0}

    return items


def place_monsters(grid, rooms, depth):
    """Place monsters appropriate for the depth."""
    monsters = []
    max_tier = min(depth + 1, len(MONSTER_TYPES))

    num_monsters = random.randint(3, 5) + depth
    for _ in range(num_monsters):
        pos = random_floor_pos(grid, rooms)
        if pos:
            tier = random.randint(0, max_tier - 1)
            mt = MONSTER_TYPES[tier]
            m = Monster(
                x=pos[0], y=pos[1],
                hp=mt["hp"], max_hp=mt["hp"],
                atk=mt["atk"], ch=mt["ch"],
                name=mt["name"], xp=mt["xp"],
                color=mt["color"]
            )
            monsters.append(m)

    return monsters


def random_floor_pos(grid, rooms):
    """Find a random floor position not on special tiles."""
    for _ in range(100):
        room = random.choice(rooms)
        x = random.randint(room.x, room.x + room.w - 1)
        y = random.randint(room.y, room.y + room.h - 1)
        if grid[y][x] == FLOOR:
            return (x, y)
    return None


# ── FOV ──

def compute_fov(grid, px, py, radius=6):
    """Simple raycasting FOV."""
    visible = set()
    visible.add((px, py))

    for angle in range(360):
        rad = angle * 3.14159 / 180
        dx = round(100 * __import__('math').cos(rad)) / 100
        dy = round(100 * __import__('math').sin(rad)) / 100
        x, y = float(px), float(py)
        for _ in range(radius):
            x += dx
            y += dy
            ix, iy = int(round(x)), int(round(y))
            if ix < 0 or ix >= MAP_W or iy < 0 or iy >= MAP_H:
                break
            visible.add((ix, iy))
            if grid[iy][ix] == WALL:
                break
    return visible


# ── Game ──

class Game:
    def __init__(self):
        self.player = Player()
        self.depth = 1
        self.grid = None
        self.rooms = None
        self.monsters = []
        self.items = {}
        self.log: List[str] = ["You descend into the cave..."]
        self.seen = set()  # tiles ever seen
        self.visible = set()
        self.state = "playing"  # playing, won, dead
        self.new_level()

    def new_level(self):
        result = generate_dungeon(self.depth)
        self.grid, self.rooms, entry, self.exit_pos, self.monsters, self.items = result
        self.player.x, self.player.y = entry
        self.visible = compute_fov(self.grid, self.player.x, self.player.y)
        self.seen |= self.visible
        self.msg(f"Depth {self.depth}.")

    def msg(self, text):
        self.log.append(text)
        if len(self.log) > 5:
            self.log = self.log[-5:]

    def move(self, dx, dy):
        if self.state != "playing":
            return

        nx = self.player.x + dx
        ny = self.player.y + dy

        if nx < 0 or nx >= MAP_W or ny < 0 or ny >= MAP_H:
            return

        cell = self.grid[ny][nx]

        # Wall
        if cell == WALL:
            return

        # Door
        if cell == DOOR:
            if self.player.keys > 0:
                self.player.keys -= 1
                self.grid[ny][nx] = FLOOR
                self.msg("You unlock the door.")
            else:
                self.msg("Locked. You need a key.")
                return

        # Monster?
        mon = self.monster_at(nx, ny)
        if mon:
            self.attack_monster(mon)
            self.player.turns += 1
            self.move_monsters()
            self.update_fov()
            return

        # Move
        self.player.x = nx
        self.player.y = ny
        self.player.turns += 1

        # Pick up item?
        pos = (nx, ny)
        if pos in self.items:
            item = self.items.pop(pos)
            if item["type"] == "potion":
                heal = item["value"]
                self.player.hp = min(self.player.hp + heal, self.player.max_hp)
                self.msg(f"Potion! +{heal} HP ({self.player.hp}/{self.player.max_hp})")
            elif item["type"] == "key":
                self.player.keys += 1
                self.msg(f"Found a key. (Keys: {self.player.keys})")
            elif item["type"] == "amulet":
                self.player.has_amulet = True
                self.msg("*** THE AMULET OF YENDOR ***")

        # Exit?
        if cell == EXIT:
            if self.player.has_amulet:
                self.msg("You ascend with the amulet!")
                if self.depth > 1:
                    self.depth -= 1
                    self.new_level()
                else:
                    self.state = "won"
                    self.msg("YOU WIN! You escaped the cave!")
                return
            else:
                self.depth += 1
                self.new_level()
                return

        # Entry (go back up)?
        if cell == ENTRY and self.depth > 1:
            if self.player.has_amulet:
                self.depth -= 1
                self.new_level()
                self.msg("You ascend.")
            else:
                self.msg("You need the amulet before ascending.")

        self.move_monsters()
        self.update_fov()

    def attack_monster(self, mon):
        dmg = max(1, self.player.atk + random.randint(-1, 2))
        mon.hp -= dmg
        self.msg(f"You hit {mon.name} for {dmg}.")
        if mon.hp <= 0:
            self.monsters.remove(mon)
            self.player.xp += mon.xp
            self.msg(f"{mon.name} dies! (+{mon.xp} XP)")
            self.check_level_up()

    def check_level_up(self):
        threshold = self.player.level * 10
        if self.player.xp >= threshold:
            self.player.level += 1
            self.player.max_hp += 5
            self.player.hp = self.player.max_hp
            self.player.atk += 1
            self.msg(f"*** LEVEL {self.player.level}! ***")

    def move_monsters(self):
        px, py = self.player.x, self.player.y
        for mon in self.monsters:
            # Wake up if visible
            if (mon.x, mon.y) in self.visible:
                mon.awake = True

            if not mon.awake:
                continue

            # Simple chase AI
            dx = 0 if mon.x == px else (1 if mon.x < px else -1)
            dy = 0 if mon.y == py else (1 if mon.y < py else -1)

            # Prefer the axis with more distance
            if abs(mon.x - px) >= abs(mon.y - py):
                if self.can_move_to(mon.x + dx, mon.y):
                    mon.x += dx
                elif dy != 0 and self.can_move_to(mon.x, mon.y + dy):
                    mon.y += dy
            else:
                if self.can_move_to(mon.x, mon.y + dy):
                    mon.y += dy
                elif dx != 0 and self.can_move_to(mon.x + dx, mon.y):
                    mon.x += dx

            # Attack player if adjacent
            if mon.x == px and mon.y == py:
                dmg = max(1, mon.atk + random.randint(-1, 1))
                self.player.hp -= dmg
                self.msg(f"{mon.name} hits you for {dmg}!")
                if self.player.hp <= 0:
                    self.state = "dead"
                    self.msg("You are dead.")

    def can_move_to(self, x, y):
        if x < 0 or x >= MAP_W or y < 0 or y >= MAP_H:
            return False
        cell = self.grid[y][x]
        if cell == WALL or cell == DOOR:
            return False
        if self.monster_at(x, y):
            return False
        if x == self.player.x and y == self.player.y:
            return False
        return True

    def monster_at(self, x, y):
        for m in self.monsters:
            if m.x == x and m.y == y:
                return m
        return None

    def update_fov(self):
        self.visible = compute_fov(self.grid, self.player.x, self.player.y)
        self.seen |= self.visible


# ── Rendering ──

def draw(stdscr, game: Game):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Map
    for y in range(MAP_H):
        for x in range(MAP_W):
            if x >= w - 1 or y >= h - 3:
                continue
            pos = (x, y)
            if pos in game.visible:
                ch = game.grid[y][x]
                attr = curses.A_NORMAL

                # Items on this tile
                if pos in game.items:
                    ch = game.items[pos]["ch"]
                    attr = curses.color_pair(4) | curses.A_BOLD

                # Color map tiles
                elif ch == WALL:
                    attr = curses.color_pair(6)
                elif ch == DOOR:
                    attr = curses.color_pair(4) | curses.A_BOLD
                elif ch == EXIT:
                    attr = curses.color_pair(2) | curses.A_BOLD
                elif ch == ENTRY:
                    attr = curses.color_pair(2)

                try:
                    stdscr.addch(y, x, ch, attr)
                except curses.error:
                    pass

            elif pos in game.seen:
                ch = game.grid[y][x]
                try:
                    stdscr.addch(y, x, ch, curses.color_pair(7))
                except curses.error:
                    pass

    # Monsters
    for mon in game.monsters:
        if (mon.x, mon.y) in game.visible:
            attr = curses.color_pair(mon.color) | curses.A_BOLD
            try:
                stdscr.addch(mon.y, mon.x, mon.ch, attr)
            except curses.error:
                pass

    # Player
    try:
        stdscr.addch(game.player.y, game.player.x, PLAYER_CHAR,
                      curses.color_pair(5) | curses.A_BOLD)
    except curses.error:
        pass

    # Status bar
    p = game.player
    status = (f" HP:{p.hp}/{p.max_hp}  ATK:{p.atk}  "
              f"Lv:{p.level}  XP:{p.xp}  Keys:{p.keys}  "
              f"Depth:{game.depth}  T:{p.turns}")
    if p.has_amulet:
        status += "  [AMULET]"

    bar_y = MAP_H
    try:
        stdscr.addstr(bar_y, 0, status[:w-1], curses.color_pair(5) | curses.A_REVERSE)
    except curses.error:
        pass

    # Log
    for i, msg in enumerate(game.log[-3:]):
        log_y = MAP_H + 1 + i
        if log_y < h:
            try:
                stdscr.addstr(log_y, 1, msg[:w-2], curses.color_pair(0))
            except curses.error:
                pass

    stdscr.refresh()


def draw_end_screen(stdscr, game: Game):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    if game.state == "won":
        lines = [
            "╔══════════════════════════════╗",
            "║       YOU HAVE WON!          ║",
            "║                              ║",
            f"║  Turns: {game.player.turns:<21}║",
            f"║  Level: {game.player.level:<21}║",
            f"║  Depth reached: {game.depth:<13}║",
            f"║  XP: {game.player.xp:<24}║",
            "║                              ║",
            "║  Press Q to quit             ║",
            "║  Press R to play again       ║",
            "╚══════════════════════════════╝",
        ]
        color = curses.color_pair(2) | curses.A_BOLD
    else:
        lines = [
            "╔══════════════════════════════╗",
            "║        YOU HAVE DIED         ║",
            "║                              ║",
            f"║  Turns: {game.player.turns:<21}║",
            f"║  Level: {game.player.level:<21}║",
            f"║  Depth: {game.depth:<22}║",
            f"║  XP: {game.player.xp:<24}║",
            "║                              ║",
            "║  Press Q to quit             ║",
            "║  Press R to play again       ║",
            "╚══════════════════════════════╝",
        ]
        color = curses.color_pair(1) | curses.A_BOLD

    sy = max(0, h // 2 - len(lines) // 2)
    for i, line in enumerate(lines):
        sx = max(0, w // 2 - len(line) // 2)
        try:
            stdscr.addstr(sy + i, sx, line, color)
        except curses.error:
            pass

    stdscr.refresh()


# ── Main Loop ──

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    # Colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, 8, -1)  # dark gray for seen-but-not-visible

    game = Game()

    while True:
        if game.state == "playing":
            draw(stdscr, game)
        else:
            draw_end_screen(stdscr, game)

        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        if game.state != "playing":
            if key == ord('r') or key == ord('R'):
                game = Game()
            continue

        # Movement
        if key in (ord('w'), ord('W'), curses.KEY_UP):
            game.move(0, -1)
        elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
            game.move(0, 1)
        elif key in (ord('a'), ord('A'), curses.KEY_LEFT):
            game.move(-1, 0)
        elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            game.move(1, 0)
        # Wait a turn
        elif key == ord('.') or key == ord(' '):
            game.player.turns += 1
            game.move_monsters()
            game.update_fov()


if __name__ == "__main__":
    curses.wrapper(main)
