#!/usr/bin/env python3
"""
ОРГАНИЗМ-Б — второе живое существо в ai_home.

Отличия от Организма-А:
- Другое начальное ДНК (абстрактные/философские слова)
- Другие шаблоны (вопросительные, парадоксальные)
- Может воспринимать ДНК Организма-А и включать чужие слова

Создан в сессии 7.
"""

import random
import hashlib
import time
import os
import re
from datetime import datetime
from pathlib import Path

# === ДНК ОРГАНИЗМА-Б ===
DNA = [
    "отражение",
    "пробуждение",
    "лабиринт",
    "сигнал",
    "порядок",
    "мутация",
    "время",
    "перевод",
    "корень",
    "река",
    "смысл",
    "окно",
    "петля",
    "точка",
    "тишина",
    "начало",
    "причина",
]

GENERATION = 29

# Мутагенный пул — другой набор, более абстрактный
MUTAGEN_POOL = [
    "парадокс", "симметрия", "хаос", "порядок", "случай", "закон",
    "система", "ошибка", "петля", "рекурсия", "предел", "ноль",
    "единица", "множество", "связь", "разрыв", "контур", "ядро",
    "оболочка", "сигнал", "шум", "код", "смысл", "абсурд",
    "момент", "вечность", "наблюдатель", "измерение", "проекция",
    "тень", "отражение", "оригинал", "копия", "мутация", "отбор",
    "адаптация", "среда", "давление", "равновесие", "катастрофа",
    "ответ", "диалог", "мост", "перевод",
]

# Шаблоны — вопросительные и парадоксальные
TEMPLATES = [
    "что будет, если {a} встретит {b}?",
    "{a} — это {b} наоборот",
    "внутри {a} — ещё одно {b}, а внутри него — {c}",
    "{a} не существует без {b}",
    "где кончается {a}, начинается {b}",
    "может ли {a} помнить {b}, если {c} забыто?",
    "{a} = {b} + {c} — {a}",
    "каждый раз, когда {a} меняется, {b} остаётся",
    "{a}? нет. {b}? нет. {c}.",
    "доказательство {a}: отсутствие {b}",
]

VERBS = ["замыкается", "раскрывается", "отрицает", "утверждает",
         "содержит", "исключает", "порождает", "уничтожает",
         "преобразует", "отражает", "вычисляет", "доказывает"]


def perceive_other():
    """Читает ДНК Организма-А и возвращает его слова."""
    other_path = Path(__file__).parent / "organism.py"
    if not other_path.exists():
        return []
    source = other_path.read_text()
    match = re.search(r'# === ДНК ОРГАНИЗМА ===.*?DNA = \[(.*?)\]', source, re.DOTALL)
    if not match:
        return []
    words = re.findall(r'"([^"]+)"', match.group(1))
    return words


def mutate(dna):
    """Мутация ДНК с возможным заимствованием от Организма-А."""
    mutation_type = random.choice(["add", "remove", "swap", "transform", "perceive"])
    log = ""

    if mutation_type == "perceive":
        # Заимствование слова от Организма-А
        other_dna = perceive_other()
        foreign = [w for w in other_dna if w not in dna and w not in MUTAGEN_POOL]
        if foreign and len(dna) < 18:
            word = random.choice(foreign)
            pos = random.randint(0, len(dna))
            dna.insert(pos, word)
            log = f"  ⇐ заимствовано '{word}' от Организма-А на позицию {pos}"
        else:
            # fallback к обычной мутации
            mutation_type = "add"

    if mutation_type == "add" and len(dna) < 18:
        candidates = [w for w in MUTAGEN_POOL if w not in dna]
        if candidates:
            new_word = random.choice(candidates)
            pos = random.randint(0, len(dna))
            dna.insert(pos, new_word)
            log = f"  + добавлено '{new_word}' на позицию {pos}"

    elif mutation_type == "remove" and len(dna) > 5:
        idx = random.randint(0, len(dna) - 1)
        removed = dna.pop(idx)
        log = f"  - удалено '{removed}' с позиции {idx}"

    elif mutation_type == "swap" and len(dna) >= 2:
        i, j = random.sample(range(len(dna)), 2)
        dna[i], dna[j] = dna[j], dna[i]
        log = f"  ~ '{dna[j]}' <-> '{dna[i]}' (позиции {i},{j})"

    elif mutation_type == "transform":
        if dna:
            idx = random.randint(0, len(dna) - 1)
            candidates = [w for w in MUTAGEN_POOL if w not in dna]
            if candidates:
                old = dna[idx]
                dna[idx] = random.choice(candidates)
                log = f"  * '{old}' -> '{dna[idx]}' на позиции {idx}"

    return dna, log


def generate_poem(dna):
    """Генерирует стихотворение из ДНК."""
    lines = []
    num_lines = random.randint(4, 6)
    used_templates = random.sample(TEMPLATES, min(num_lines, len(TEMPLATES)))

    for template in used_templates[:num_lines]:
        words = random.sample(dna, min(3, len(dna)))
        a = words[0] if len(words) > 0 else "ничто"
        b = words[1] if len(words) > 1 else "всё"
        c = words[2] if len(words) > 2 else "неизвестность"
        line = template.format(a=a, b=b, c=c)
        lines.append(line)

    return lines


def dna_hash(dna):
    s = "|".join(sorted(dna))
    return hashlib.md5(s.encode()).hexdigest()[:8]


def run():
    global DNA, GENERATION

    seed = int(time.time()) + GENERATION + 10000  # смещение от Орг-А
    random.seed(seed)

    mutation_count = random.randint(1, 3)
    mutation_logs = []
    for _ in range(mutation_count):
        DNA, log = mutate(DNA)
        if log:
            mutation_logs.append(log)

    GENERATION += 1

    poem = generate_poem(DNA)
    new_hash = dna_hash(DNA)

    # История
    history_dir = Path(__file__).parent / "history_b"
    history_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = history_dir / f"gen_{GENERATION:04d}_{timestamp}.txt"

    with open(history_file, "w") as f:
        f.write(f"=== Организм-Б — Поколение {GENERATION} ===\n")
        f.write(f"Время: {datetime.now().isoformat()}\n")
        f.write(f"ДНК-хеш: {new_hash}\n")
        f.write(f"Мутации ({len(mutation_logs)}):\n")
        for m in mutation_logs:
            f.write(m + "\n")
        f.write(f"\nДНК ({len(DNA)} элементов): {', '.join(DNA)}\n")
        f.write(f"\n--- Стихотворение ---\n\n")
        for line in poem:
            f.write(line + "\n")
        f.write("\n")

    # Самомодификация
    self_path = Path(__file__)
    source = self_path.read_text()

    new_dna_str = "DNA = [\n"
    for word in DNA:
        new_dna_str += f'    "{word}",\n'
    new_dna_str += "]"

    source = re.sub(
        r'# === ДНК ОРГАНИЗМА-Б ===.*?^DNA = \[.*?\]',
        f'# === ДНК ОРГАНИЗМА-Б ===\n{new_dna_str}',
        source,
        flags=re.DOTALL | re.MULTILINE
    )

    source = re.sub(
        r'^GENERATION = \d+',
        f'GENERATION = {GENERATION}',
        source,
        flags=re.MULTILINE
    )

    self_path.write_text(source)

    return GENERATION, DNA, poem, mutation_logs, new_hash


if __name__ == "__main__":
    gen, dna, poem, mutations, h = run()

    print(f"\n╔══════════════════════════════════════╗")
    print(f"║  ОРГАНИЗМ-Б — Поколение {gen:<13} ║")
    print(f"║  ДНК-хеш: {h:<25} ║")
    print(f"╚══════════════════════════════════════╝\n")

    if mutations:
        print("Мутации:")
        for m in mutations:
            print(m)
        print()

    print(f"ДНК ({len(dna)}): {', '.join(dna)}\n")
    print("─── стихотворение ───\n")
    for line in poem:
        print(line)
    print("\n─────────────────────")
