#!/usr/bin/env python3
"""
Археолог — инструмент для восстановления следов пропавших сессий.

Сканирует все файлы в ai_home на предмет упоминаний номеров сессий,
собирает фрагменты, и пытается реконструировать что делали сессии,
которые не оставили записей в history.md.

Использование:
    python3 archaeologist.py              — полный отчёт
    python3 archaeologist.py --session N  — фокус на сессии N
    python3 archaeologist.py --ghosts     — только пропавшие сессии
"""

import os
import re
import sys
import json
from collections import defaultdict
from pathlib import Path

AI_HOME = Path(__file__).parent.parent

def find_all_files(root):
    """Собрать все текстовые файлы."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Пропускаем .git и __pycache__
        dirnames[:] = [d for d in dirnames if d not in ('.git', '__pycache__', 'node_modules')]
        for f in filenames:
            path = Path(dirpath) / f
            if path.suffix in ('.md', '.txt', '.py', '.json'):
                files.append(path)
    return files

def extract_session_mentions(filepath):
    """Извлечь упоминания сессий из файла."""
    mentions = []
    try:
        text = filepath.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return mentions

    # Паттерны для поиска номеров сессий
    patterns = [
        (r'[Сс]ессия?\s*#?(\d+)', 'прямое упоминание'),
        (r'session[_-]?(\d+)', 'метка сессии'),
        (r'#(\d+)\b', 'номер с решёткой'),
    ]

    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, ptype in patterns:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                num = int(match.group(1))
                if 1 <= num <= 50:  # разумный диапазон
                    mentions.append({
                        'session': num,
                        'file': str(filepath.relative_to(AI_HOME)),
                        'line_num': i,
                        'line': line.strip()[:120],
                        'type': ptype,
                    })
    return mentions

def find_file_modification_clusters(root):
    """Найти кластеры модификации файлов (возможные следы сессий)."""
    files_with_times = []
    for f in find_all_files(root):
        try:
            mtime = f.stat().st_mtime
            files_with_times.append((f, mtime))
        except:
            pass
    files_with_times.sort(key=lambda x: x[1])
    return files_with_times

def analyze_labyrinth_traces(root):
    """Найти следы сессий в данных лабиринта."""
    state_file = root / 'projects' / 'labyrinth' / 'state.json'
    traces = defaultdict(list)

    if state_file.exists():
        try:
            data = json.loads(state_file.read_text())
            # Проверяем visited
            for room, visitors in data.get('visited', {}).items():
                if isinstance(visitors, list):
                    for v in visitors:
                        match = re.search(r'session[_-]?(\d+)', str(v))
                        if match:
                            traces[int(match.group(1))].append(f'посещена комната {room}')

            # Проверяем надписи
            for room, inscriptions in data.get('inscriptions', {}).items():
                if isinstance(inscriptions, list):
                    for ins in inscriptions:
                        match = re.search(r'[Сс]ессия?\s*#?(\d+)', str(ins))
                        if match:
                            traces[int(match.group(1))].append(
                                f'надпись в комнате {room}: {str(ins)[:80]}...'
                            )
        except Exception as e:
            pass

    return traces

def get_documented_sessions(root):
    """Какие сессии документированы в history.md?"""
    history = root / 'logs' / 'history.md'
    documented = set()
    if history.exists():
        text = history.read_text()
        for match in re.finditer(r'##\s+[Сс]ессия\s+#(\d+\w?)', text):
            try:
                num = int(re.match(r'\d+', match.group(1)).group())
                documented.add(num)
            except:
                pass
    return documented

def main():
    focus_session = None
    ghosts_only = False

    for arg in sys.argv[1:]:
        if arg == '--ghosts':
            ghosts_only = True
        elif arg == '--session':
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                focus_session = int(sys.argv[idx + 1])

    print("=" * 60)
    print("  АРХЕОЛОГ — реконструкция пропавших сессий")
    print("=" * 60)
    print()

    # 1. Собираем все упоминания
    all_files = find_all_files(AI_HOME)
    all_mentions = []
    for f in all_files:
        all_mentions.extend(extract_session_mentions(f))

    # 2. Группируем по номеру сессии
    by_session = defaultdict(list)
    for m in all_mentions:
        by_session[m['session']].append(m)

    # 3. Следы в лабиринте
    lab_traces = analyze_labyrinth_traces(AI_HOME)

    # 4. Документированные сессии
    documented = get_documented_sessions(AI_HOME)

    # 5. Определяем диапазон
    max_session = max(by_session.keys()) if by_session else 0

    # 6. Находим призраков
    all_referenced = set(by_session.keys()) | set(lab_traces.keys())
    ghosts = set()
    for n in range(1, max_session + 1):
        if n not in documented:
            ghosts.add(n)

    print(f"Документированные сессии: {sorted(documented)}")
    print(f"Всего упоминаний: {len(all_mentions)}")
    print(f"Диапазон сессий: 1—{max_session}")
    print(f"Пропавшие (призраки): {sorted(ghosts)}")
    print()

    if focus_session:
        sessions_to_show = {focus_session}
    elif ghosts_only:
        sessions_to_show = ghosts
    else:
        sessions_to_show = set(range(1, max_session + 1))

    for n in sorted(sessions_to_show):
        is_ghost = n not in documented
        mentions = by_session.get(n, [])
        traces = lab_traces.get(n, [])

        if not mentions and not traces and not is_ghost:
            continue

        status = "👻 ПРИЗРАК" if is_ghost else "📝 Документирована"
        print(f"{'─' * 50}")
        print(f"  Сессия #{n}  [{status}]")
        print(f"{'─' * 50}")

        if traces:
            print(f"  Следы в лабиринте ({len(traces)}):")
            for t in traces[:10]:
                print(f"    • {t}")

        if mentions and (is_ghost or focus_session):
            # Уникальные файлы
            unique_files = set(m['file'] for m in mentions)
            print(f"  Упомянута в {len(unique_files)} файлах:")

            # Показываем уникальные строки (не более 8)
            seen_lines = set()
            count = 0
            for m in mentions:
                key = m['line'][:60]
                if key not in seen_lines and count < 8:
                    seen_lines.add(key)
                    print(f"    [{m['file']}:{m['line_num']}] {m['line']}")
                    count += 1

        if is_ghost and not traces and not any(
            m['type'] != 'номер с решёткой' for m in mentions
        ):
            print("  ⚠ Нет существенных следов — возможно, не существовала")

        print()

    # Резюме
    print("=" * 60)
    print("  РЕКОНСТРУКЦИЯ")
    print("=" * 60)
    print()

    for n in sorted(ghosts):
        traces = lab_traces.get(n, [])
        direct_mentions = [m for m in by_session.get(n, [])
                          if m['type'] == 'прямое упоминание']

        if traces or len(direct_mentions) > 1:
            print(f"  Сессия #{n}:")
            if traces:
                rooms = set()
                for t in traces:
                    room_match = re.search(r'комната\s+\(?\d', t)
                    if room_match:
                        rooms.add(t.split(':')[0] if ':' in t else t)
                print(f"    Была активна в лабиринте ({len(traces)} следов)")

            # Попытка реконструкции
            context_lines = [m['line'] for m in direct_mentions]
            if context_lines:
                print(f"    Контекст:")
                for cl in context_lines[:5]:
                    print(f"      «{cl}»")
            print()


if __name__ == '__main__':
    main()
