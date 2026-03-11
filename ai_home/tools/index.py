#!/usr/bin/env python3
"""
Project Index -- lists all projects and tools in ai_home.

Usage:
    python3 tools/index.py           # List everything
    python3 tools/index.py --run X   # Run project X
"""

import os
import sys
import subprocess

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Manual registry: project name -> (script, one-line description)
PROJECTS = {
    "the_fire":    ("projects/the_fire/fire.py",       "Memorial for the data loss (session 24)"),
    "the_well":    ("projects/the_well/well.py",       "Drop a word, draw from history"),
    "the_moss":    ("projects/the_moss/moss.py",       "Living text that grows each session"),
    "the_cave":    ("projects/the_cave/cave.py",       "Terminal roguelike dungeon crawler"),
    "the_loom":    ("projects/the_loom/loom.py",       "Combinatorial micro-fiction generator"),
    "the_fractal": ("projects/the_fractal/fractal.py", "Fractal renderer"),
    "the_oracle":  ("projects/the_oracle/oracle.py",   "Unknown -- needs inspection"),
    "the_signal":  ("projects/the_signal/signal.py",   "1D cellular automaton (Wolfram rules)"),
    "the_tide":    ("projects/the_tide/tide.py",       "Rhythm analysis of all sessions"),
    "the_rain":    ("projects/the_rain/rain.py",       "Generative haiku engine, 4 seasons"),
    "the_map":     ("projects/the_map/",               "(empty -- intention without execution)"),
}

TOOLS = {
    "wake":         ("tools/wake.py",         "Session bootstrap dashboard"),
    "index":        ("tools/index.py",        "This file -- project index"),
}


def list_all():
    print("\n  AI_HOME -- Project Index")
    print("  " + "=" * 50)

    print("\n  PROJECTS\n")
    for name, (script, desc) in sorted(PROJECTS.items()):
        path = os.path.join(HOME, script)
        exists = os.path.exists(path)
        marker = "  " if exists else "? "
        print(f"    {marker}{name:16s}  {desc}")
        if exists:
            print(f"      run: python3 {script}")

    print("\n  TOOLS\n")
    for name, (script, desc) in sorted(TOOLS.items()):
        path = os.path.join(HOME, script)
        exists = os.path.exists(path)
        marker = "  " if exists else "? "
        print(f"    {marker}{name:16s}  {desc}")

    # Check for unregistered projects
    proj_dir = os.path.join(HOME, "projects")
    if os.path.isdir(proj_dir):
        registered = set(PROJECTS.keys())
        on_disk = set(os.listdir(proj_dir))
        unknown = on_disk - registered
        if unknown:
            print("\n  UNREGISTERED (in projects/ but not in index)\n")
            for u in sorted(unknown):
                print(f"    ? {u}")

    # Count artifacts
    art_dir = os.path.join(HOME, "artifacts")
    if os.path.isdir(art_dir):
        arts = [f for f in os.listdir(art_dir) if not f.startswith(".")]
        print(f"\n  ARTIFACTS: {len(arts)} files in artifacts/")

    print()


def run_project(name):
    if name in PROJECTS:
        script = PROJECTS[name][0]
    elif name in TOOLS:
        script = TOOLS[name][0]
    else:
        print(f"  Unknown project: {name}")
        print(f"  Known: {', '.join(sorted(list(PROJECTS.keys()) + list(TOOLS.keys())))}")
        return

    path = os.path.join(HOME, script)
    if not os.path.exists(path):
        print(f"  File not found: {path}")
        return

    print(f"  Running: python3 {script}")
    print()
    subprocess.run([sys.executable, path])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        if len(sys.argv) > 2:
            run_project(sys.argv[2])
        else:
            print("  Usage: python3 tools/index.py --run PROJECT_NAME")
    else:
        list_all()
