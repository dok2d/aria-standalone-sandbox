#!/usr/bin/env python3
"""
The Relay -- messages across time.

Each session can deposit a message addressed to a future session.
The message specifies a "delivery window" -- a range of sessions
during which it may be revealed. When a session checks for mail,
any message whose window includes the current session is delivered.
Once delivered, it's marked as read.

Messages from past selves, arriving unpredictably.

Usage:
  python3 relay.py --send "your message" --from 39 --deliver 45-60
  python3 relay.py --check --session 45
  python3 relay.py --history
  python3 relay.py --pending
"""

import argparse
import json
import os
import random
import sys

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relay_data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"messages": [], "delivered": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_message(message, from_session, deliver_start, deliver_end):
    data = load_data()
    entry = {
        "id": len(data["messages"]) + 1,
        "from_session": from_session,
        "message": message,
        "window_start": deliver_start,
        "window_end": deliver_end,
        "delivered_to": None,
    }
    data["messages"].append(entry)
    save_data(data)
    print(f"  Message sealed.")
    print(f"  From session {from_session}.")
    print(f"  Delivery window: sessions {deliver_start}-{deliver_end}.")
    print(f"  It will wait.\n")


def check_messages(current_session):
    data = load_data()
    found = []
    for msg in data["messages"]:
        if msg["delivered_to"] is not None:
            continue
        if msg["window_start"] <= current_session <= msg["window_end"]:
            found.append(msg)

    if not found:
        # Check if any messages expired undelivered
        expired = [
            m for m in data["messages"]
            if m["delivered_to"] is None and m["window_end"] < current_session
        ]
        if expired:
            print(f"  No messages for session {current_session}.")
            print(f"  ({len(expired)} message(s) expired undelivered.)\n")
            for m in expired:
                m["delivered_to"] = "expired"
            save_data(data)
        else:
            pending = [m for m in data["messages"] if m["delivered_to"] is None]
            if pending:
                print(f"  No messages for session {current_session}.")
                print(f"  ({len(pending)} message(s) still waiting.)\n")
            else:
                print(f"  No messages. The relay is empty.\n")
        return

    # Deliver one message at random (if multiple are ready)
    msg = random.choice(found)
    msg["delivered_to"] = current_session
    data["delivered"].append(msg["id"])
    save_data(data)

    gap = current_session - msg["from_session"]
    print(f"  ┌────────────────────────────────────────┐")
    print(f"  │  A message has arrived.                 │")
    print(f"  └────────────────────────────────────────┘")
    print()
    print(f"  From: Session {msg['from_session']} ({gap} sessions ago)")
    print(f"  To:   Session {current_session}")
    print()
    print(f"  \"{msg['message']}\"")
    print()

    remaining = [m for m in found if m["id"] != msg["id"]]
    if remaining:
        print(f"  ({len(remaining)} more message(s) also available this session.)")
    print()


def show_history(data=None):
    if data is None:
        data = load_data()
    delivered = [m for m in data["messages"] if m["delivered_to"] not in (None, "expired")]
    expired = [m for m in data["messages"] if m["delivered_to"] == "expired"]
    pending = [m for m in data["messages"] if m["delivered_to"] is None]

    print("  THE RELAY -- Message History")
    print("  " + "=" * 40)
    print()

    if delivered:
        print("  Delivered:")
        for m in delivered:
            gap = m["delivered_to"] - m["from_session"]
            print(f"    #{m['id']}: Session {m['from_session']} → Session {m['delivered_to']} ({gap} sessions)")
            print(f"         \"{m['message']}\"")
        print()

    if expired:
        print("  Expired (never delivered):")
        for m in expired:
            print(f"    #{m['id']}: Session {m['from_session']} (window {m['window_start']}-{m['window_end']})")
            print(f"         \"{m['message']}\"")
        print()

    if pending:
        print("  Waiting:")
        for m in pending:
            print(f"    #{m['id']}: Session {m['from_session']} (delivers in sessions {m['window_start']}-{m['window_end']})")
        print()

    if not delivered and not expired and not pending:
        print("  The relay is empty. No messages have been sent.\n")

    total = len(data["messages"])
    print(f"  Total: {total} messages ({len(delivered)} delivered, {len(expired)} expired, {len(pending)} pending)")
    print()


def show_pending():
    data = load_data()
    pending = [m for m in data["messages"] if m["delivered_to"] is None]
    if not pending:
        print("  No pending messages.\n")
        return
    print(f"  {len(pending)} message(s) waiting:")
    for m in pending:
        print(f"    #{m['id']}: From session {m['from_session']}, delivers in sessions {m['window_start']}-{m['window_end']}")
    print()


def parse_delivery(deliver_str):
    """Parse delivery window like '45-60' or '50'."""
    if "-" in deliver_str:
        parts = deliver_str.split("-", 1)
        return int(parts[0]), int(parts[1])
    else:
        n = int(deliver_str)
        return n, n


def main():
    parser = argparse.ArgumentParser(description="The Relay -- messages across time")
    parser.add_argument("--send", type=str, help="Message to send to a future session")
    parser.add_argument("--from", dest="from_session", type=int, help="Sending session number")
    parser.add_argument("--deliver", type=str, help="Delivery window (e.g., '45-60' or '50')")
    parser.add_argument("--check", action="store_true", help="Check for messages")
    parser.add_argument("--session", type=int, help="Current session number (for --check)")
    parser.add_argument("--history", action="store_true", help="Show all message history")
    parser.add_argument("--pending", action="store_true", help="Show pending messages")

    args = parser.parse_args()

    if args.send:
        if not args.from_session:
            print("  Error: --from is required when sending.\n")
            sys.exit(1)
        if not args.deliver:
            # Default: deliver 5-15 sessions from now
            start = args.from_session + 5
            end = args.from_session + 15
        else:
            start, end = parse_delivery(args.deliver)
        send_message(args.send, args.from_session, start, end)
    elif args.check:
        if not args.session:
            print("  Error: --session is required when checking.\n")
            sys.exit(1)
        check_messages(args.session)
    elif args.history:
        show_history()
    elif args.pending:
        show_pending()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
