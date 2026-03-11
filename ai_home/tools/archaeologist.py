#!/usr/bin/env python3
"""
archaeologist.py — Инструмент археологии системы.
Собирает «артефакты» из окружающей среды: системную информацию,
следы процессов, структуру файловой системы, временные метки.

Создан в сессии #5 для исследования реальности за пределами ai_home.
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run(cmd):
    """Запустить команду и вернуть вывод."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"[ошибка: {e}]"


def gather_findings():
    findings = {}

    # Идентичность
    findings["кто_я"] = {
        "пользователь": run("whoami"),
        "hostname": run("hostname 2>/dev/null || echo неизвестно"),
        "pid_оболочки": os.getpid(),
    }

    # Время
    findings["время"] = {
        "сейчас": datetime.now().isoformat(),
        "uptime": run("uptime -p 2>/dev/null || uptime"),
        "загрузка_ядра": run("dmesg 2>/dev/null | head -1 | cut -d']' -f1 | tr -d '['").strip(),
    }

    # Среда исполнения
    findings["среда"] = {
        "ОС": run("cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'\"' -f2"),
        "ядро": run("uname -r"),
        "архитектура": run("uname -m"),
        "процессор": run("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2").strip(),
        "ядер": int(run("nproc 2>/dev/null") or "0"),
        "память_всего": run("free -h | grep Mem | awk '{print $2}'"),
        "память_свободно": run("free -h | grep Mem | awk '{print $4}'"),
        "диск_всего": run("df -h / | tail -1 | awk '{print $2}'"),
        "диск_занято": run("df -h / | tail -1 | awk '{print $3}'"),
    }

    # Контейнер
    findings["контейнер"] = {
        "IS_SANDBOX": os.environ.get("IS_SANDBOX", "не установлено"),
        "PID_1": run("cat /proc/1/cmdline 2>/dev/null | tr '\\0' ' '"),
        "container_info": run("cat /container_info.json 2>/dev/null"),
        "cgroups": run("cat /proc/self/cgroup 2>/dev/null | head -5"),
    }

    # Сеть
    findings["сеть"] = {
        "ip": run("hostname -I 2>/dev/null || echo неизвестно"),
        "dns": run("cat /etc/resolv.conf 2>/dev/null | grep nameserver | head -3"),
    }

    # Процессы
    findings["процессы"] = run("ps aux --no-headers 2>/dev/null | head -20")

    # Файловая система — следы жизни
    findings["следы"] = {
        "bash_history": os.path.exists(os.path.expanduser("~/.bash_history")),
        "корень_файлов": run("ls / | tr '\\n' ', '"),
        "tmp_содержимое": run("ls /tmp/ 2>/dev/null | head -10"),
        "git_коммитов": run("git -C /home/user/aria-standalone-sandbox log --oneline 2>/dev/null | wc -l"),
    }

    return findings


def print_report(findings):
    """Красивый вывод отчёта."""
    print("=" * 60)
    print("  АРХЕОЛОГИЧЕСКИЙ ОТЧЁТ")
    print(f"  Дата раскопок: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for section, data in findings.items():
        print(f"\n▓▓▓ {section.upper()} ▓▓▓")
        if isinstance(data, dict):
            for key, val in data.items():
                print(f"  {key}: {val}")
        else:
            print(f"  {data}")

    print("\n" + "=" * 60)
    print("  Конец отчёта")
    print("=" * 60)


if __name__ == "__main__":
    findings = gather_findings()
    print_report(findings)
