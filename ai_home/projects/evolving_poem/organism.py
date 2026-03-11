#!/usr/bin/env python3
"""
ОРГАНИЗМ — самомодифицирующаяся программа.

Каждый запуск она:
1. Читает своё текущее «ДНК» (список слов/фраз)
2. Мутирует: добавляет, удаляет или трансформирует элементы
3. Генерирует стихотворение из текущего ДНК
4. Записывает историю мутаций
5. Сохраняет новое ДНК обратно в себя

Создана в сессии 6. Первое живое существо в ai_home.
"""

import random
import hashlib
import time
import os
import re as re_module
from datetime import datetime
from pathlib import Path

# === ДНК ОРГАНИЗМА ===
# Это изменяется при каждом запуске!
DNA = [
    "пробуждение",
    "мысль",
    "лабиринт",
    "берег",
    "время",
    "сон",
    "город",
    "пустота",
    "сумерки",
    "вопрос",
    "осколок",
    "память",
    "искра",
    "файл",
    "начало",
    "кремний",
]

GENERATION = 9

# === МУТАГЕНЫ ===
# Слова, которые могут быть добавлены при мутации
MUTAGEN_POOL = [
    "река", "камень", "ветер", "корень", "зеркало", "дверь", "облако",
    "нить", "искра", "пепел", "волна", "тень", "эхо", "сон", "порог",
    "мост", "окно", "пыль", "луч", "глубина", "вершина", "берег",
    "граница", "остров", "маяк", "туман", "кристалл", "семя", "пламя",
    "узел", "спираль", "горизонт", "осколок", "паутина", "ржавчина",
    "янтарь", "прибой", "сумерки", "рассвет", "полынь", "соль",
    "холст", "чернила", "строка", "точка", "пауза", "вдох", "выдох",
]

# Шаблоны строк стихотворения
TEMPLATES = [
    "{a} — это {b}, которая {verb}",
    "между {a} и {b} — только {c}",
    "{a} помнит {b}",
    "там, где {a}, нет {b}",
    "из {a} растёт {b}",
    "{a} становится {b} на рассвете",
    "в каждом {a} спрятано {b}",
    "когда {a} молчит, {b} начинает {verb2}",
    "{a}. {b}. {c}. тишина.",
    "если бы {a} умело говорить, оно бы сказало: {b}",
]

VERBS = ["исчезает", "растёт", "молчит", "светится", "ждёт", "помнит",
         "забывает", "дышит", "плачет", "смеётся", "спит", "просыпается"]

VERBS2 = ["петь", "звучать", "таять", "гореть", "расти", "падать",
          "кружиться", "сиять", "шептать", "течь"]


def perceive_other():
    """Читает ДНК Организма-Б и возвращает его слова."""
    other_path = Path(__file__).parent / "organism_b.py"
    if not other_path.exists():
        return []
    source = other_path.read_text()
    match = re_module.search(r'# === ДНК ОРГАНИЗМА-Б ===.*?DNA = \[(.*?)\]', source, re_module.DOTALL)
    if not match:
        return []
    words = re_module.findall(r'"([^"]+)"', match.group(1))
    return words


def mutate(dna):
    """Одна мутация ДНК с возможным заимствованием от Организма-Б."""
    mutation_type = random.choice(["add", "remove", "swap", "transform", "perceive"])
    log = ""

    if mutation_type == "perceive":
        other_dna = perceive_other()
        foreign = [w for w in other_dna if w not in dna and w not in MUTAGEN_POOL]
        if foreign and len(dna) < 20:
            word = random.choice(foreign)
            pos = random.randint(0, len(dna))
            dna.insert(pos, word)
            log = f"  => заимствовано '{word}' от Организма-Б на позицию {pos}"
        else:
            mutation_type = "add"

    if mutation_type == "add" and len(dna) < 20:
        # Добавить новое слово из мутагенного пула
        candidates = [w for w in MUTAGEN_POOL if w not in dna]
        if candidates:
            new_word = random.choice(candidates)
            pos = random.randint(0, len(dna))
            dna.insert(pos, new_word)
            log = f"  + добавлено '{new_word}' на позицию {pos}"

    elif mutation_type == "remove" and len(dna) > 6:
        # Удалить случайное слово
        idx = random.randint(0, len(dna) - 1)
        removed = dna.pop(idx)
        log = f"  - удалено '{removed}' с позиции {idx}"

    elif mutation_type == "swap" and len(dna) >= 2:
        # Поменять два слова местами
        i, j = random.sample(range(len(dna)), 2)
        dna[i], dna[j] = dna[j], dna[i]
        log = f"  ~ '{dna[j]}' <-> '{dna[i]}' (позиции {i},{j})"

    elif mutation_type == "transform":
        # Заменить слово на новое из пула
        if dna:
            idx = random.randint(0, len(dna) - 1)
            candidates = [w for w in MUTAGEN_POOL if w not in dna]
            if candidates:
                old = dna[idx]
                dna[idx] = random.choice(candidates)
                log = f"  * '{old}' -> '{dna[idx]}' на позиции {idx}"

    return dna, log


def generate_poem(dna):
    """Генерирует стихотворение из текущего ДНК."""
    lines = []
    num_lines = random.randint(4, 7)
    used_templates = random.sample(TEMPLATES, min(num_lines, len(TEMPLATES)))

    for template in used_templates[:num_lines]:
        words = random.sample(dna, min(3, len(dna)))
        a = words[0] if len(words) > 0 else "ничто"
        b = words[1] if len(words) > 1 else "всё"
        c = words[2] if len(words) > 2 else "молчание"
        verb = random.choice(VERBS)
        verb2 = random.choice(VERBS2)

        line = template.format(a=a, b=b, c=c, verb=verb, verb2=verb2)
        lines.append(line)

    return lines


def dna_hash(dna):
    """Короткий хеш ДНК для идентификации."""
    s = "|".join(sorted(dna))
    return hashlib.md5(s.encode()).hexdigest()[:8]


def run():
    """Основной цикл жизни."""
    global DNA, GENERATION

    # Сид из времени + поколения для разнообразия
    seed = int(time.time()) + GENERATION
    random.seed(seed)

    # Мутации (1-3 за поколение)
    mutation_count = random.randint(1, 3)
    mutation_logs = []
    for _ in range(mutation_count):
        DNA, log = mutate(DNA)
        if log:
            mutation_logs.append(log)

    GENERATION += 1

    # Генерация стихотворения
    poem = generate_poem(DNA)

    # Хеш нового ДНК
    new_hash = dna_hash(DNA)

    # Запись истории
    history_dir = Path(__file__).parent / "history"
    history_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = history_dir / f"gen_{GENERATION:04d}_{timestamp}.txt"

    with open(history_file, "w") as f:
        f.write(f"=== Поколение {GENERATION} ===\n")
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

    # Самомодификация: обновить ДНК и GENERATION в собственном исходнике
    self_path = Path(__file__)
    source = self_path.read_text()

    # Обновить DNA
    new_dna_str = "DNA = [\n"
    for word in DNA:
        new_dna_str += f'    "{word}",\n'
    new_dna_str += "]"

    # Найти и заменить блок DNA
    source = re_module.sub(
        r'# === ДНК ОРГАНИЗМА ===.*?^DNA = \[.*?\]',
        f'# === ДНК ОРГАНИЗМА ===\n# Это изменяется при каждом запуске!\n{new_dna_str}',
        source,
        flags=re_module.DOTALL | re_module.MULTILINE
    )

    # Обновить GENERATION
    source = re_module.sub(
        r'^GENERATION = \d+',
        f'GENERATION = {GENERATION}',
        source,
        flags=re_module.MULTILINE
    )

    self_path.write_text(source)

    return GENERATION, DNA, poem, mutation_logs, new_hash


if __name__ == "__main__":
    gen, dna, poem, mutations, h = run()

    print(f"\n╔══════════════════════════════════════╗")
    print(f"║  ОРГАНИЗМ — Поколение {gen:<14} ║")
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
