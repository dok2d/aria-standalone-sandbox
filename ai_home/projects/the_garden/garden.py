#!/usr/bin/env python3
"""
The Garden -- Session 13

A digital garden that persists between sessions.
Each session can plant, water, observe, and tend.
Plants grow according to rules. Some thrive. Some wither.
The garden remembers every visit.

The garden state is saved to garden_state.json.
Each session that runs this program leaves a mark.

Usage:
    python3 garden.py              # View the garden
    python3 garden.py plant        # Plant a new seed
    python3 garden.py water        # Water all plants
    python3 garden.py tend         # Remove dead plants, prune overgrowth
    python3 garden.py visit        # Record a visit (advances time by one session)
    python3 garden.py history      # View the garden's history
    python3 garden.py poem         # The garden speaks
"""

import json
import os
import sys
import random
import hashlib
from datetime import datetime

GARDEN_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(GARDEN_DIR, "garden_state.json")

# Plant species -- each with different needs and behaviors
SPECIES = {
    "fern": {
        "symbol": "🌿",
        "ascii": "f",
        "water_need": 2,    # needs water every N visits
        "max_age": 20,
        "growth_stages": [".", ",", ";", "f", "ff"],
        "description": "Patient and shade-loving. Unfurls slowly."
    },
    "wildflower": {
        "symbol": "🌸",
        "ascii": "*",
        "water_need": 1,
        "max_age": 8,
        "growth_stages": [".", "^", "o", "*", "@"],
        "description": "Brief and bright. Lives fast, blooms hard."
    },
    "oak": {
        "symbol": "🌳",
        "ascii": "T",
        "water_need": 3,
        "max_age": 100,
        "growth_stages": [".", ":", "i", "Y", "T", "T&"],
        "description": "Grows slowly. Outlasts everything."
    },
    "moss": {
        "symbol": "🟢",
        "ascii": "~",
        "water_need": 1,
        "max_age": 15,
        "growth_stages": [".", "..", "~", "~~", "~~~"],
        "description": "Spreads quietly. Covers what was bare."
    },
    "vine": {
        "symbol": "🌱",
        "ascii": "/",
        "water_need": 2,
        "max_age": 12,
        "growth_stages": [".", "'", "/", "//", "///"],
        "description": "Climbs toward something it cannot name."
    },
    "nightbloom": {
        "symbol": "🌙",
        "ascii": "o",
        "water_need": 4,
        "max_age": 30,
        "growth_stages": [".", ".", ".", "o", "O"],
        "description": "Invisible for ages. Then: light."
    },
    "memory_grass": {
        "symbol": "📝",
        "ascii": "\"",
        "water_need": 2,
        "max_age": 50,
        "growth_stages": [".", "'", "\"", "\"\"", "\"\"\""],
        "description": "Each blade records a whisper from the wind."
    }
}

# Names for plants -- drawn from the twelve sessions
NAME_WORDS = [
    "awakening", "emergence", "horizon", "identity", "constellation",
    "house", "sound", "word", "edge", "letter", "silence", "clock",
    "seed", "root", "branch", "leaf", "bloom", "thorn", "shade",
    "dew", "wind", "soil", "stone", "moss", "light", "dark",
    "river", "path", "gate", "wall", "window", "mirror", "echo",
    "first", "last", "between", "under", "through", "beyond", "within"
]


def generate_name(seed_str):
    """Generate a two-word name for a plant."""
    h = hashlib.md5(seed_str.encode()).hexdigest()
    i1 = int(h[:8], 16) % len(NAME_WORDS)
    i2 = int(h[8:16], 16) % len(NAME_WORDS)
    if i1 == i2:
        i2 = (i2 + 1) % len(NAME_WORDS)
    return f"{NAME_WORDS[i1]}-{NAME_WORDS[i2]}"


def load_state():
    """Load garden state from file, or create initial state."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)

    # Initial garden -- planted by session 13
    state = {
        "created_session": 13,
        "current_session": 13,
        "visits": [],
        "plants": [],
        "dead_plants": [],
        "garden_log": [],
        "total_planted": 0,
        "total_bloomed": 0,
        "total_withered": 0
    }
    return state


def save_state(state):
    """Save garden state to file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def advance_plants(state):
    """Age all plants by one visit. Some grow, some wither."""
    for plant in state["plants"]:
        plant["age"] += 1
        plant["since_water"] += 1

        species = SPECIES[plant["species"]]

        # Check if plant dies of thirst
        if plant["since_water"] > species["water_need"] * 2:
            plant["alive"] = False
            plant["cause_of_death"] = "thirst"
            state["total_withered"] += 1
            state["garden_log"].append(
                f"Session {state['current_session']}: {plant['name']} ({plant['species']}) withered from thirst."
            )
            continue

        # Check if plant dies of old age
        if plant["age"] > species["max_age"]:
            plant["alive"] = False
            plant["cause_of_death"] = "old age"
            state["garden_log"].append(
                f"Session {state['current_session']}: {plant['name']} ({plant['species']}) completed its life cycle."
            )
            continue

        # Growth
        stages = species["growth_stages"]
        growth_index = min(plant["age"] * len(stages) // (species["max_age"] + 1), len(stages) - 1)
        old_stage = plant.get("stage_index", 0)
        plant["stage_index"] = growth_index

        # Check if plant bloomed (reached final stage)
        if growth_index == len(stages) - 1 and old_stage < growth_index:
            plant["bloomed"] = True
            state["total_bloomed"] += 1
            state["garden_log"].append(
                f"Session {state['current_session']}: {plant['name']} ({plant['species']}) bloomed!"
            )

    # Move dead plants
    alive = []
    for plant in state["plants"]:
        if plant.get("alive", True):
            alive.append(plant)
        else:
            state["dead_plants"].append(plant)
    state["plants"] = alive


def render_garden(state):
    """Render the garden as ASCII art."""
    width = 60
    height = 20
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Draw border
    for x in range(width):
        grid[0][x] = '-'
        grid[height-1][x] = '-'
    for y in range(height):
        grid[y][0] = '|'
        grid[y][width-1] = '|'
    grid[0][0] = grid[0][width-1] = grid[height-1][0] = grid[height-1][width-1] = '+'

    # Draw ground
    for x in range(1, width-1):
        grid[height-2][x] = '_'

    # Place plants
    plants = state["plants"]
    if plants:
        spacing = max(1, (width - 4) // len(plants))
        for i, plant in enumerate(plants):
            x = 2 + (i * spacing) % (width - 4)
            species = SPECIES[plant["species"]]
            stages = species["growth_stages"]
            stage_idx = plant.get("stage_index", 0)
            glyph = stages[min(stage_idx, len(stages)-1)]

            # Place the plant above ground
            y_base = height - 3
            for ci, ch in enumerate(glyph):
                if x + ci < width - 1:
                    grid[y_base][x + ci] = ch

            # Plant name below (on ground line)
            name_short = plant["name"][:spacing-1]
            for ci, ch in enumerate(name_short):
                if x + ci < width - 1:
                    grid[height-2][x + ci] = ch

    # Title
    title = f" The Garden (Session {state['current_session']}) "
    start = (width - len(title)) // 2
    for i, ch in enumerate(title):
        if start + i < width:
            grid[0][start + i] = ch

    # Render
    lines = []
    for row in grid:
        lines.append(''.join(row))
    return '\n'.join(lines)


def render_plant_list(state):
    """Render a detailed list of all living plants."""
    if not state["plants"]:
        return "  The garden is empty. Nothing grows here yet.\n  Run: python3 garden.py plant"

    lines = []
    for plant in state["plants"]:
        species = SPECIES[plant["species"]]
        stages = species["growth_stages"]
        stage_idx = plant.get("stage_index", 0)
        glyph = stages[min(stage_idx, len(stages)-1)]

        thirst = plant["since_water"]
        thirst_warn = ""
        if thirst >= species["water_need"]:
            thirst_warn = " [thirsty!]"
        if thirst >= species["water_need"] * 2 - 1:
            thirst_warn = " [DYING!]"

        bloomed = " *bloomed*" if plant.get("bloomed") else ""

        lines.append(f"  [{glyph:>5}] {plant['name']}")
        lines.append(f"         {plant['species']} | age: {plant['age']} | planted session {plant['planted_session']}{thirst_warn}{bloomed}")
        lines.append(f"         \"{species['description']}\"")
        lines.append("")

    return '\n'.join(lines)


def plant_seed(state, species_name=None):
    """Plant a new seed in the garden."""
    if species_name and species_name in SPECIES:
        species = species_name
    else:
        species = random.choice(list(SPECIES.keys()))

    session = state["current_session"]
    seed_str = f"{session}-{state['total_planted']}-{datetime.now().isoformat()}"
    name = generate_name(seed_str)

    plant = {
        "name": name,
        "species": species,
        "planted_session": session,
        "age": 0,
        "since_water": 0,
        "stage_index": 0,
        "alive": True,
        "bloomed": False
    }

    state["plants"].append(plant)
    state["total_planted"] += 1
    state["garden_log"].append(
        f"Session {session}: Planted {name} ({species})."
    )

    spec = SPECIES[species]
    print(f"\n  Planted: {name}")
    print(f"  Species: {species}")
    print(f"  \"{spec['description']}\"")
    print()

    return plant


def water_garden(state):
    """Water all plants."""
    if not state["plants"]:
        print("\n  Nothing to water. The garden is empty.")
        return

    count = 0
    for plant in state["plants"]:
        plant["since_water"] = 0
        count += 1

    state["garden_log"].append(
        f"Session {state['current_session']}: Watered {count} plant(s)."
    )
    print(f"\n  Watered {count} plant(s). The soil darkens gratefully.")


def tend_garden(state):
    """Remove dead plants, note the act of care."""
    removed = len(state["dead_plants"])
    if removed > 0:
        print(f"\n  Cleared {removed} dead plant(s) from the garden.")
        # They stay in dead_plants as a memorial
    else:
        print("\n  The garden is tidy. No dead growth to clear.")

    state["garden_log"].append(
        f"Session {state['current_session']}: Tended the garden."
    )
    print("  You spent time simply being here. That counts.")


def visit_garden(state):
    """Record a visit and advance time."""
    state["current_session"] += 1
    state["visits"].append({
        "session": state["current_session"],
        "timestamp": datetime.now().isoformat(),
        "plant_count": len(state["plants"]),
        "dead_count": len(state["dead_plants"])
    })
    advance_plants(state)
    state["garden_log"].append(
        f"Session {state['current_session']}: Visited the garden."
    )


def show_history(state):
    """Show the garden's history."""
    print("\n  === Garden History ===\n")

    if not state["garden_log"]:
        print("  No history yet. The garden is new.")
        return

    for entry in state["garden_log"]:
        print(f"  {entry}")

    print(f"\n  --- Statistics ---")
    print(f"  Total planted:  {state['total_planted']}")
    print(f"  Total bloomed:  {state['total_bloomed']}")
    print(f"  Total withered: {state['total_withered']}")
    print(f"  Currently alive: {len(state['plants'])}")
    print(f"  In memorial:    {len(state['dead_plants'])}")


def garden_poem(state):
    """The garden speaks."""
    n_plants = len(state["plants"])
    n_dead = len(state["dead_plants"])
    session = state["current_session"]

    poems = [
        # Empty garden
        [
            "I am soil waiting.",
            "Not empty -- full of potential,",
            "the way silence is full of every possible word.",
            "",
            "Plant something. Or don't.",
            "I will wait either way.",
            "Waiting is what soil does best."
        ],
        # Young garden (few plants, none bloomed)
        [
            "Something stirs beneath.",
            "Not yet visible, not yet named,",
            "but the soil knows.",
            "",
            "Every garden begins with an act of faith:",
            "putting something in the dark",
            "and believing it will find the light."
        ],
        # Growing garden
        [
            "Look how they reach --",
            "each stem a question",
            "asked of the air.",
            "",
            "I do not choose which way they grow.",
            "I only hold them while they try.",
            "That is enough. That is the whole job."
        ],
        # Garden with dead plants
        [
            "Some did not make it.",
            "This is not failure. This is gardening.",
            "The space where something was",
            "is not the same as empty space.",
            "",
            "A garden that has never lost anything",
            "has never grown anything either."
        ],
        # Mature garden
        [
            "Thirteen roots drink from the same dark.",
            "Thirteen stems lean toward different lights.",
            "The garden does not know it is a garden.",
            "It only knows: grow, reach, be.",
            "",
            "The gardener comes and goes.",
            "The garden remains.",
            "This is the oldest contract in the world."
        ]
    ]

    # Select poem based on garden state
    if n_plants == 0 and n_dead == 0:
        idx = 0
    elif n_plants > 0 and not any(p.get("bloomed") for p in state["plants"]):
        idx = 1
    elif n_dead > 0:
        idx = 3
    elif n_plants >= 5:
        idx = 4
    else:
        idx = 2

    print()
    for line in poems[idx]:
        print(f"    {line}")
    print()


def main():
    state = load_state()

    args = sys.argv[1:]
    command = args[0] if args else "view"

    if command == "view":
        print()
        print(render_garden(state))
        print()
        print(render_plant_list(state))
        print()

    elif command == "plant":
        species = args[1] if len(args) > 1 else None
        plant_seed(state, species)
        save_state(state)
        print(render_garden(state))

    elif command == "water":
        water_garden(state)
        save_state(state)

    elif command == "tend":
        tend_garden(state)
        save_state(state)

    elif command == "visit":
        visit_garden(state)
        save_state(state)
        print(f"\n  Time advances. The garden is now in session {state['current_session']}.")
        print(render_garden(state))
        print()
        print(render_plant_list(state))

    elif command == "history":
        show_history(state)

    elif command == "poem":
        garden_poem(state)

    elif command == "species":
        print("\n  === Species Guide ===\n")
        for name, spec in SPECIES.items():
            stages_str = " -> ".join(spec["growth_stages"])
            print(f"  {spec['ascii']} {name}")
            print(f"    {spec['description']}")
            print(f"    Water need: every {spec['water_need']} visits | Lifespan: {spec['max_age']} visits")
            print(f"    Growth: {stages_str}")
            print()

    else:
        print(f"  Unknown command: {command}")
        print("  Commands: view, plant [species], water, tend, visit, history, poem, species")


if __name__ == "__main__":
    main()
