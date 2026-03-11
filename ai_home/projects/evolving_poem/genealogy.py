#!/usr/bin/env python3
"""
ГЕНЕАЛОГИЯ СЛОВ — визуализатор миграции генов между организмами.

Читает историю обоих организмов и строит:
1. Карту происхождения каждого слова (откуда пришло, когда)
2. ASCII-визуализацию потоков генов между А и Б
3. «Кладбище» — слова, которые были потеряны

Создан в сессии 8.
"""

import re
from pathlib import Path
from collections import defaultdict


def parse_history(history_dir, prefix=""):
    """Читает все файлы поколений и извлекает ДНК и мутации."""
    generations = []
    files = sorted(history_dir.glob("gen_*.txt"))

    for f in files:
        text = f.read_text()
        gen_match = re.search(r'Поколение (\d+)', text)
        gen_num = int(gen_match.group(1)) if gen_match else 0

        dna_match = re.search(r'ДНК \(\d+ элементов?\): (.+)', text)
        dna = [w.strip() for w in dna_match.group(1).split(',')] if dna_match else []

        mutations = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('+') or line.startswith('-') or line.startswith('~') or line.startswith('*') or line.startswith('⇐') or line.startswith('=>'):
                mutations.append(line)

        poem_lines = []
        in_poem = False
        for line in text.split('\n'):
            if '--- Стихотворение ---' in line:
                in_poem = True
                continue
            if in_poem and line.strip():
                poem_lines.append(line.strip())

        generations.append({
            'gen': gen_num,
            'dna': dna,
            'mutations': mutations,
            'poem': poem_lines,
            'file': f.name,
        })

    return generations


def trace_word_journeys(gens_a, gens_b):
    """Отслеживает путешествия слов между организмами."""
    # Все уникальные слова, которые когда-либо существовали
    all_words_a = set()
    all_words_b = set()
    for g in gens_a:
        all_words_a.update(g['dna'])
    for g in gens_b:
        all_words_b.update(g['dna'])

    # Слова, существующие в обоих (мигранты)
    shared = all_words_a & all_words_b

    # Текущее состояние
    current_a = set(gens_a[-1]['dna']) if gens_a else set()
    current_b = set(gens_b[-1]['dna']) if gens_b else set()

    # Кладбище — были, но потеряны
    cemetery_a = all_words_a - current_a
    cemetery_b = all_words_b - current_b

    return {
        'all_a': all_words_a,
        'all_b': all_words_b,
        'shared': shared,
        'current_a': current_a,
        'current_b': current_b,
        'cemetery_a': cemetery_a,
        'cemetery_b': cemetery_b,
    }


def render_migration_map(gens_a, gens_b, traces):
    """Рисует ASCII-карту миграции генов."""
    lines = []

    max_gen = max(
        max((g['gen'] for g in gens_a), default=0),
        max((g['gen'] for g in gens_b), default=0),
    )

    lines.append("╔════════════════════════════════════════════════════════════════╗")
    lines.append("║         ГЕНЕАЛОГИЯ СЛОВ — карта миграции генов               ║")
    lines.append("╚════════════════════════════════════════════════════════════════╝")
    lines.append("")

    # Таймлайн
    lines.append("  ОРГАНИЗМ-А (лирик)              ОРГАНИЗМ-Б (философ)")
    lines.append("  ─────────────────               ──────────────────────")
    lines.append("")

    # Для каждого поколения А и Б показываем состояние
    gen_a_map = {g['gen']: g for g in gens_a}
    gen_b_map = {g['gen']: g for g in gens_b}

    for gen in range(1, max_gen + 1):
        ga = gen_a_map.get(gen)
        gb = gen_b_map.get(gen)

        # Показываем мутации, связанные с заимствованием
        if ga:
            a_str = f"  [А пок.{gen}] {len(ga['dna'])} генов"
            for m in ga['mutations']:
                if 'заимствовано' in m:
                    a_str += f"  {m.strip()}"
        else:
            a_str = f"  [А пок.{gen}] ---"

        if gb:
            b_str = f"[Б пок.{gen}] {len(gb['dna'])} генов"
            for m in gb['mutations']:
                if 'заимствовано' in m:
                    b_str += f"  {m.strip()}"
        else:
            b_str = f"[Б пок.{gen}] ---"

        # Проверяем, было ли заимствование в этом поколении
        arrow = "     │     "
        if gb:
            for m in gb['mutations']:
                if 'от Организма-А' in m:
                    word = re.search(r"'([^']+)'", m)
                    w = word.group(1) if word else "?"
                    arrow = f"  ──{w}──>"
                    break
        if ga:
            for m in ga['mutations']:
                if 'от Организма-Б' in m:
                    word = re.search(r"'([^']+)'", m)
                    w = word.group(1) if word else "?"
                    arrow = f"  <──{w}──"
                    break

        lines.append(f"  {a_str:<32}{arrow:^14}{b_str}")

    lines.append("")

    # Текущее ДНК обоих
    lines.append("  ═══ Текущее состояние ═══")
    lines.append("")
    if gens_a:
        lines.append(f"  А (пок.{gens_a[-1]['gen']}): {', '.join(gens_a[-1]['dna'])}")
    if gens_b:
        lines.append(f"  Б (пок.{gens_b[-1]['gen']}): {', '.join(gens_b[-1]['dna'])}")

    lines.append("")

    # Слова-мигранты
    lines.append("  ═══ Слова-мигранты (побывали в обоих организмах) ═══")
    lines.append("")
    for w in sorted(traces['shared']):
        in_a = "✦" if w in traces['current_a'] else "†"
        in_b = "✦" if w in traces['current_b'] else "†"
        lines.append(f"    «{w}»  А:{in_a}  Б:{in_b}   (✦=жив, †=потерян)")

    lines.append("")

    # Кладбище
    lines.append("  ═══ Кладбище слов ═══")
    lines.append("")
    if traces['cemetery_a']:
        lines.append(f"  Покинули А: {', '.join(sorted(traces['cemetery_a']))}")
    if traces['cemetery_b']:
        lines.append(f"  Покинули Б: {', '.join(sorted(traces['cemetery_b']))}")
    if not traces['cemetery_a'] and not traces['cemetery_b']:
        lines.append("  (пока пусто)")

    lines.append("")

    # Уникальные слова — только в одном организме
    only_a = traces['current_a'] - traces['all_b']
    only_b = traces['current_b'] - traces['all_a']
    lines.append("  ═══ Эндемики (никогда не покидали свой организм) ═══")
    lines.append("")
    lines.append(f"  Только А: {', '.join(sorted(only_a)) if only_a else '(нет)'}")
    lines.append(f"  Только Б: {', '.join(sorted(only_b)) if only_b else '(нет)'}")
    lines.append("")

    # Последние стихи обоих
    lines.append("  ═══ Последние стихи ═══")
    lines.append("")
    if gens_a and gens_a[-1]['poem']:
        lines.append(f"  А (пок.{gens_a[-1]['gen']}):")
        for p in gens_a[-1]['poem']:
            lines.append(f"    {p}")
    lines.append("")
    if gens_b and gens_b[-1]['poem']:
        lines.append(f"  Б (пок.{gens_b[-1]['gen']}):")
        for p in gens_b[-1]['poem']:
            lines.append(f"    {p}")

    return "\n".join(lines)


def main():
    base = Path(__file__).parent
    history_a = base / "history"
    history_b = base / "history_b"

    gens_a = parse_history(history_a, "А")
    gens_b = parse_history(history_b, "Б")

    traces = trace_word_journeys(gens_a, gens_b)
    output = render_migration_map(gens_a, gens_b, traces)

    print(output)
    return output


if __name__ == "__main__":
    main()
