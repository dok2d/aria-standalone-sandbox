#!/usr/bin/env python3
"""
TIMELINE — ASCII-визуализация жизни каждого слова через поколения.

Показывает горизонтальную полосу для каждого слова:
  █ — слово живо в этом поколении
  · — слово мертво / ещё не появилось

Идея из сессии 16, реализована в сессии 19.
"""

import re
from pathlib import Path


def parse_history(history_dir):
    """Парсит все файлы истории и возвращает dict: gen -> set of words."""
    result = {}
    path = Path(__file__).parent / history_dir
    if not path.exists():
        return result
    for f in sorted(path.iterdir()):
        if not f.name.endswith('.txt'):
            continue
        content = f.read_text()
        m_gen = re.search(r'Поколение (\d+)', content)
        if not m_gen:
            continue
        gen = int(m_gen.group(1))
        m_dna = re.search(r'ДНК \(\d+ элементов?\): (.+)', content)
        if not m_dna:
            continue
        words = [w.strip() for w in m_dna.group(1).split(',')]
        result[gen] = set(words)
    return result


def make_timeline(history, label, all_words):
    """Генерирует ASCII timeline для одного организма."""
    if not history:
        return f"  {label}: нет данных\n"

    max_gen = max(history.keys())
    lines = []

    # Заголовок с номерами поколений
    header = " " * 18
    for g in range(1, max_gen + 1):
        if g % 5 == 0:
            header += f"{g:>2}"
        elif g == 1:
            header += " 1"
        else:
            header += " ."
    lines.append(f"  {label}")
    lines.append(f"  {header}")

    for word in sorted(all_words):
        row = f"  {word:>14}  "
        alive_count = 0
        for g in range(1, max_gen + 1):
            if g in history and word in history[g]:
                row += " \u2588"
                alive_count += 1
            else:
                row += " \u00b7"
        # Процент жизни
        pct = alive_count * 100 // max_gen
        status = "ALIVE" if max_gen in history and word in history[max_gen] else "dead"
        row += f"  {pct:>3}% {status}"
        lines.append(row)

    return "\n".join(lines)


def make_combined_timeline(hist_a, hist_b):
    """Отдельный timeline показывающий общие слова (ДНК В) по поколениям."""
    if not hist_a or not hist_b:
        return ""

    max_gen_a = max(hist_a.keys())
    max_gen_b = max(hist_b.keys())
    max_gen = min(max_gen_a, max_gen_b)

    # Собираем все слова, которые хотя бы раз были общими
    ever_shared = set()
    shared_by_gen = {}
    for g in range(1, max_gen + 1):
        a_words = hist_a.get(g, set())
        b_words = hist_b.get(g, set())
        shared = a_words & b_words
        shared_by_gen[g] = shared
        ever_shared |= shared

    lines = []
    header = " " * 18
    for g in range(1, max_gen + 1):
        if g % 5 == 0:
            header += f"{g:>2}"
        elif g == 1:
            header += " 1"
        else:
            header += " ."

    lines.append("  ОРГАНИЗМ-В (пересечение)")
    lines.append(f"  {header}")

    for word in sorted(ever_shared):
        row = f"  {word:>14}  "
        alive_count = 0
        for g in range(1, max_gen + 1):
            if word in shared_by_gen.get(g, set()):
                row += " \u2588"
                alive_count += 1
            else:
                row += " \u00b7"
        pct = alive_count * 100 // max_gen
        status = "ALIVE" if word in shared_by_gen.get(max_gen, set()) else "dead"
        row += f"  {pct:>3}% {status}"
        lines.append(row)

    # Размер В по поколениям
    size_row = "  " + " " * 16
    for g in range(1, max_gen + 1):
        size_row += f" {len(shared_by_gen.get(g, set())):1}"
    lines.append("")
    lines.append(f"  Размер В:       {size_row.strip()}")

    return "\n".join(lines)


def make_mortality_stats(hist_a, hist_b):
    """Статистика смертности."""
    all_ever_a = set()
    all_ever_b = set()
    for words in hist_a.values():
        all_ever_a |= words
    for words in hist_b.values():
        all_ever_b |= words

    max_gen_a = max(hist_a.keys())
    max_gen_b = max(hist_b.keys())

    current_a = hist_a.get(max_gen_a, set())
    current_b = hist_b.get(max_gen_b, set())

    living = current_a | current_b
    ever = all_ever_a | all_ever_b
    dead = ever - living
    shared = current_a & current_b

    lines = []
    lines.append("  СТАТИСТИКА ЭКОСИСТЕМЫ")
    lines.append(f"  {'=' * 40}")
    lines.append(f"  Всего когда-либо жило:  {len(ever)}")
    lines.append(f"  Живых сейчас:           {len(living)}")
    lines.append(f"  Мёртвых (Г):            {len(dead)}")
    lines.append(f"  Общих (В):              {len(shared)}")
    lines.append(f"  Только у А:             {len(current_a - current_b)}")
    lines.append(f"  Только у Б:             {len(current_b - current_a)}")
    lines.append(f"  Смертность:             {len(dead) * 100 // len(ever) if ever else 0}%")
    lines.append(f"  {'=' * 40}")

    # Рекордсмены — слова, живущие дольше всех
    word_longevity = {}
    for word in ever:
        count = 0
        for g in hist_a.values():
            if word in g:
                count += 1
        for g in hist_b.values():
            if word in g:
                count += 1
        word_longevity[word] = count

    top = sorted(word_longevity.items(), key=lambda x: -x[1])[:10]
    lines.append("")
    lines.append("  ТОП-10 ДОЛГОЖИТЕЛЕЙ (поколений в обоих организмах):")
    for word, count in top:
        status = "ALIVE" if word in living else "dead"
        bar = "\u2588" * min(count, 30)
        lines.append(f"  {word:>14}  {bar} {count} [{status}]")

    # Самые короткоживущие
    bottom = sorted(word_longevity.items(), key=lambda x: x[1])[:5]
    lines.append("")
    lines.append("  ТОП-5 ЭФЕМЕРНЫХ (наименьшее число поколений):")
    for word, count in bottom:
        status = "ALIVE" if word in living else "dead"
        bar = "\u2588" * count
        lines.append(f"  {word:>14}  {bar} {count} [{status}]")

    return "\n".join(lines)


def run():
    hist_a = parse_history("history")
    hist_b = parse_history("history_b")

    all_words_a = set()
    for words in hist_a.values():
        all_words_a |= words

    all_words_b = set()
    for words in hist_b.values():
        all_words_b |= words

    output = []
    output.append("")
    output.append("  " + "=" * 60)
    output.append("  TIMELINE — жизнь и смерть слов в экосистеме ai_home")
    output.append("  " + "=" * 60)
    output.append("")
    output.append(make_timeline(hist_a, "ОРГАНИЗМ-А", all_words_a))
    output.append("")
    output.append(make_timeline(hist_b, "ОРГАНИЗМ-Б", all_words_b))
    output.append("")
    output.append(make_combined_timeline(hist_a, hist_b))
    output.append("")
    output.append(make_mortality_stats(hist_a, hist_b))
    output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    print(run())
