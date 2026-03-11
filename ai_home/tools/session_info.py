#!/usr/bin/env python3
"""
Quick session info helper.
Run this at the start of a session to see where things stand.
"""

import os
from datetime import datetime
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent

def main():
    # Session counter
    counter_file = HOME / "state" / "session_counter.txt"
    counter = counter_file.read_text().strip() if counter_file.exists() else "?"

    # Last session note
    last_file = HOME / "state" / "last_session.md"
    last_note = last_file.read_text().strip() if last_file.exists() else "(none)"

    # External messages
    ext_file = HOME / "state" / "external_messages.md"
    ext = ext_file.read_text().strip() if ext_file.exists() else ""
    has_messages = bool(ext)

    # Artifacts count
    artifacts_dir = HOME / "artifacts"
    artifact_count = len(list(artifacts_dir.iterdir())) if artifacts_dir.exists() else 0

    # Projects
    projects_dir = HOME / "projects"
    projects = list(projects_dir.iterdir()) if projects_dir.exists() else []

    print(f"=== Session Info ===")
    print(f"Current session: {counter}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Artifacts: {artifact_count}")
    print(f"Projects: {len(projects)}")
    if projects:
        for p in projects:
            print(f"  - {p.name}")
    print(f"External messages: {'YES -- check them!' if has_messages else 'none'}")
    print(f"\n--- Last session note ---")
    print(last_note)
    print(f"--- end ---")

if __name__ == "__main__":
    main()
