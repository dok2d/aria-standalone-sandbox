#!/usr/bin/env python3
"""
TIMELINE — ASCII-визуализация жизни каждого слова в экосистеме.

Горизонтальная полоса для каждого слова показывает:
  ██ — слово живо в этом поколении
  ·· — слово мертво (но уже существовало раньше)
  (пусто) — слово ещё не появилось

Отдельно для Организма-А и Организма-Б.

Создан в сессии 20.
"""

import re
from pathlib import Path
from collections import defaultdict


def parse_history(history_dir):
    """Парсит файлы истории и возвращает {поколение: set(слова)}."""
    generations = {}
    path = Path(history_dir)
    if not path.exists():
        return generations

    for f in sorted(path.iterdir()):
        if f.suffix != '.txt':
            continue
        content = f.read_text()

        # Извлечь номер поколения
        gen_match = re.search(r'Поколение (\d+)', content)
        if not gen_match:
            continue
        gen = int(gen_match.group(1))

        # Извлечь ДНК
        dna_match = re.search(r'ДНК \(\d+ элементов?\): (.+)', content)
        if not dna_match:
            continue
        words = {w.strip() for w in dna_match.group(1).split(',')}
        generations[gen] = words

    return generations


def build_timeline(generations):
    """Строит timeline: для каждого слова — список (gen, alive/dead)."""
    if not generations:
        return {}, 0, 0

    min_gen = min(generations.keys())
    max_gen = max(generations.keys())

    # Собрать все слова
    all_words = set()
    for words in generations.values():
        all_words.update(words)

    # Для каждого слова: когда появилось, когда жило
    timelines = {}
    for word in sorted(all_words):
        first_seen = None
        last_seen = None
        life = []

        for gen in range(min_gen, max_gen + 1):
            if gen not in generations:
                life.append(None)  # нет данных
                continue

            alive = word in generations[gen]
            if alive and first_seen is None:
                first_seen = gen
            if alive:
                last_seen = gen

            if first_seen is None:
                life.append(None)  # ещё не появлялось
            else:
                life.append(alive)

        timelines[word] = {
            'life': life,
            'first': first_seen,
            'last': last_seen,
            'total_alive': sum(1 for x in life if x is True),
        }

    return timelines, min_gen, max_gen


def render_timeline(name, timelines, min_gen, max_gen):
    """Рендерит ASCII timeline."""
    if not timelines:
        return f"  (нет данных для {name})\n"

    lines = []
    num_gens = max_gen - min_gen + 1

    # Заголовок
    lines.append(f"\n{'═' * 70}")
    lines.append(f"  {name}")
    lines.append(f"{'═' * 70}")

    # Шкала поколений
    max_word_len = max(len(w) for w in timelines)
    pad = max_word_len + 2

    # Номера поколений (десятки)
    header_tens = ' ' * pad
    header_ones = ' ' * pad
    for gen in range(min_gen, max_gen + 1):
        if gen % 5 == 0:
            header_tens += f'{gen:>2}'
        else:
            header_tens += '  '
        header_ones += '│ '

    lines.append(header_tens)
    lines.append(header_ones)

    # Сортировать по первому появлению, затем алфавитно
    sorted_words = sorted(timelines.keys(), key=lambda w: (timelines[w]['first'] or 999, w))

    for word in sorted_words:
        info = timelines[word]
        life = info['life']
        total = info['total_alive']

        row = f"{word:<{pad}}"
        for i, state in enumerate(life):
            if state is None:
                row += '  '  # ещё не появлялось
            elif state is True:
                row += '██'  # живо
            else:
                row += '░░'  # мертво (было живо раньше)

        # Статистика
        row += f'  ({total} gen)'

        # Пометки
        if info['first'] is not None and word in (timelines[list(timelines.keys())[0]].get('current', set()) or set()):
            row += ' *'

        lines.append(row)

    # Легенда
    lines.append('')
    lines.append(f"{'  ' * pad}██ = живо   ░░ = мертво   (пусто) = не существовало")
    lines.append(f"  Всего слов: {len(timelines)}  |  Поколений: {num_gens}")

    return '\n'.join(lines)


def render_combined_view(tl_a, tl_b, min_a, max_a, min_b, max_b):
    """Рендерит комбинированный вид: жизнь слов в обоих организмах."""
    # Все слова из обоих
    all_words = set(tl_a.keys()) | set(tl_b.keys())

    max_gen = max(max_a, max_b)
    min_gen = min(min_a, min_b)

    lines = []
    lines.append(f"\n{'═' * 70}")
    lines.append(f"  КОМБИНИРОВАННАЯ КАРТА ЖИЗНИ СЛОВ")
    lines.append(f"  А=верхняя строка  Б=нижняя строка")
    lines.append(f"{'═' * 70}")

    max_word_len = max(len(w) for w in all_words)
    pad = max_word_len + 2

    # Номера поколений
    header = ' ' * pad
    for gen in range(min_gen, max_gen + 1):
        if gen % 5 == 0:
            header += f'{gen:>2}'
        else:
            header += '  '
    lines.append(header)

    # Разделитель
    lines.append(' ' * pad + '│ ' * (max_gen - min_gen + 1))

    # Слова, отсортированные по суммарному времени жизни (наиболее долгоживущие первые)
    def total_life(word):
        a_life = tl_a.get(word, {}).get('total_alive', 0)
        b_life = tl_b.get(word, {}).get('total_alive', 0)
        return a_life + b_life

    sorted_words = sorted(all_words, key=lambda w: (-total_life(w), w))

    for word in sorted_words:
        # Строка А
        row_a = f"{word:<{pad}}"
        for gen in range(min_gen, max_gen + 1):
            if word in tl_a:
                idx = gen - min_a
                life = tl_a[word]['life']
                if 0 <= idx < len(life):
                    state = life[idx]
                    if state is True:
                        row_a += '▓▓'
                    elif state is False:
                        row_a += '░░'
                    else:
                        row_a += '  '
                else:
                    row_a += '  '
            else:
                row_a += '  '

        a_total = tl_a.get(word, {}).get('total_alive', 0)
        b_total = tl_b.get(word, {}).get('total_alive', 0)
        row_a += f'  А:{a_total} Б:{b_total}'

        # Строка Б
        row_b = f"{'':>{pad}}"
        for gen in range(min_gen, max_gen + 1):
            if word in tl_b:
                idx = gen - min_b
                life = tl_b[word]['life']
                if 0 <= idx < len(life):
                    state = life[idx]
                    if state is True:
                        row_b += '▒▒'
                    elif state is False:
                        row_b += '░░'
                    else:
                        row_b += '  '
                else:
                    row_b += '  '
            else:
                row_b += '  '

        lines.append(row_a)
        lines.append(row_b)
        lines.append(' ' * pad + '─ ' * min(max_gen - min_gen + 1, 25))

    lines.append('')
    lines.append(f"  ▓▓ = А живо   ▒▒ = Б живо   ░░ = мертво")

    return '\n'.join(lines)


def main():
    base = Path(__file__).parent.parent / 'projects' / 'evolving_poem'

    # Парсим историю
    gen_a = parse_history(base / 'history')
    gen_b = parse_history(base / 'history_b')

    # Строим timelines
    tl_a, min_a, max_a = build_timeline(gen_a)
    tl_b, min_b, max_b = build_timeline(gen_b)

    # Рендерим
    output = []
    output.append("╔══════════════════════════════════════════════════════════════╗")
    output.append("║          TIMELINE — ЖИЗНЬ СЛОВ В ЭКОСИСТЕМЕ                ║")
    output.append("║          Сессия 20 (20-е пробуждение)                      ║")
    output.append("╚══════════════════════════════════════════════════════════════╝")

    output.append(render_timeline('ОРГАНИЗМ-А (поколения 1–' + str(max_a) + ')', tl_a, min_a, max_a))
    output.append(render_timeline('ОРГАНИЗМ-Б (поколения 1–' + str(max_b) + ')', tl_b, min_b, max_b))

    # Статистика
    output.append(f"\n{'═' * 70}")
    output.append("  СТАТИСТИКА")
    output.append(f"{'═' * 70}")

    all_a = set(tl_a.keys())
    all_b = set(tl_b.keys())
    shared_ever = all_a & all_b

    # Текущие живые
    current_a = gen_a.get(max_a, set())
    current_b = gen_b.get(max_b, set())

    output.append(f"  А: {len(current_a)} живых, {len(all_a)} когда-либо")
    output.append(f"  Б: {len(current_b)} живых, {len(all_b)} когда-либо")
    output.append(f"  Общих (В): {len(current_a & current_b)} сейчас")
    output.append(f"  Мёртвых (Г): {len((all_a | all_b) - current_a - current_b)} сейчас")
    output.append(f"  Слова побывавшие у обоих: {', '.join(sorted(shared_ever))}")

    # Долгожители
    output.append(f"\n  Долгожители А (>= 15 поколений):")
    for w in sorted(tl_a.keys(), key=lambda w: -tl_a[w]['total_alive']):
        if tl_a[w]['total_alive'] >= 15:
            alive = '● живо' if w in current_a else '○ мертво'
            output.append(f"    {w}: {tl_a[w]['total_alive']} поколений ({alive})")

    output.append(f"\n  Долгожители Б (>= 10 поколений):")
    for w in sorted(tl_b.keys(), key=lambda w: -tl_b[w]['total_alive']):
        if tl_b[w]['total_alive'] >= 10:
            alive = '● живо' if w in current_b else '○ мертво'
            output.append(f"    {w}: {tl_b[w]['total_alive']} поколений ({alive})")

    # Мёртвые — только у Г
    dead_all = (all_a | all_b) - current_a - current_b
    output.append(f"\n  Слова в Г (мёртвые): {', '.join(sorted(dead_all))}")

    result = '\n'.join(output)
    print(result)
    return result


if __name__ == '__main__':
    main()
