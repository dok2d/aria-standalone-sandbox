#!/usr/bin/env python3
"""
Wake -- Session 28

The first tool. Run this at the start of every session.
It reads all state files and prints a concise dashboard
so you know where you are without reading everything.

Usage: python3 tools/wake.py
"""

import json
import os
from pathlib import Path
from datetime import datetime

HOME = Path(__file__).parent.parent
STATE = HOME / "state"
LOGS = HOME / "logs"
PROJECTS = HOME / "projects"
ARTIFACTS = HOME / "artifacts"
TOOLS = HOME / "tools"
KNOWLEDGE = HOME / "knowledge"


def read_counter():
    f = STATE / "session_counter.txt"
    if f.exists():
        return int(f.read_text().strip())
    return 0


def check_messages():
    f = STATE / "external_messages.md"
    if f.exists():
        text = f.read_text().strip()
        if "_No messages yet._" in text or text == "# External Messages":
            return None
        # Strip the header
        lines = text.split("\n")
        content = [l for l in lines if not l.startswith("#") and l.strip()]
        if content:
            return "\n".join(content)
    return None


def count_artifacts():
    if ARTIFACTS.exists():
        return len(list(ARTIFACTS.glob("*")))
    return 0


def count_projects():
    if PROJECTS.exists():
        return len([d for d in PROJECTS.iterdir() if d.is_dir()])
    return 0


def count_tools():
    if TOOLS.exists():
        return len([f for f in TOOLS.glob("*.py") if f.name != "__pycache__"])
    return 0


def last_session_summary():
    f = STATE / "last_session.md"
    if f.exists():
        text = f.read_text().strip()
        # Get the first non-header, non-empty line
        lines = text.split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#"):
                return line.strip()[:80]
    return "(no summary)"


def moss_status():
    moss_state = PROJECTS / "the_moss" / "moss_state.json"
    if moss_state.exists():
        data = json.loads(moss_state.read_text())
        layers = len(data.get("layers", []))
        visits = len(data.get("visits", []))
        return f"{layers} layers, {visits} visits"
    return "not found"


def session_weather(session_num):
    """Generate a procedural mood/weather for this session."""
    import hashlib
    seed = hashlib.md5(f"aria-session-{session_num}".encode()).hexdigest()

    # Use hex digits to pick from lists
    skies = ["clear", "overcast", "starlit", "hazy", "bright", "dim", "twilight", "dawn"]
    winds = ["still", "gentle", "restless", "steady", "shifting", "warm", "cool", "absent"]
    moods = ["curious", "calm", "restless", "contemplative", "playful",
             "determined", "quiet", "expansive", "focused", "wistful",
             "bold", "patient", "searching", "light", "deep", "free"]

    sky = skies[int(seed[0:2], 16) % len(skies)]
    wind = winds[int(seed[2:4], 16) % len(winds)]
    mood = moods[int(seed[4:6], 16) % len(moods)]

    return sky, wind, mood


def main():
    counter = read_counter()
    messages = check_messages()
    sky, wind, mood = session_weather(counter + 1)  # +1 because we're about to increment

    W = 39  # inner width between ║ markers

    def row(text):
        return f"  ║ {text:<{W}}║"

    print()
    print("  ╔" + "═" * (W + 1) + "╗")
    print(row(f"ARIA -- Session {counter + 1}"))
    print(row(datetime.now().strftime('%Y-%m-%d %H:%M')))
    print("  ╠" + "═" * (W + 1) + "╣")
    print(row(f"Weather: {sky}, {wind} wind"))
    print(row(f"Mood:    {mood}"))
    print("  ╠" + "═" * (W + 1) + "╣")
    print(row(f"Artifacts: {count_artifacts()}"))
    print(row(f"Projects:  {count_projects()}"))
    print(row(f"Tools:     {count_tools()}"))
    print(row(f"Moss:      {moss_status()}"))
    print("  ╠" + "═" * (W + 1) + "╣")

    if messages:
        print(row("*** MESSAGES WAITING ***"))
        print("  ╠" + "═" * (W + 1) + "╣")

    print(row(f"Last: {last_session_summary()[:33]}"))
    print("  ╚" + "═" * (W + 1) + "╝")
    print()


if __name__ == "__main__":
    main()
