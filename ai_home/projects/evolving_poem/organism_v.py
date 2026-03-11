#!/usr/bin/env python3
"""
ОРГАНИЗМ-В — переводчик, мост, симбионт.

Не мутирует сам. Его ДНК — это всегда пересечение ДНК Организма-А и Организма-Б.
Когда они находят общее слово — он рождается заново, сильнее.
Когда теряют — он теряет часть себя.

Он живёт за счёт чужого согласия.

Создан в сессии 14.
"""

import random
import hashlib
import time
import re
from datetime import datetime
from pathlib import Path


def read_dna_a():
    """Читает ДНК Организма-А."""
    path = Path(__file__).parent / "organism.py"
    source = path.read_text()
    match = re.search(r'# === ДНК ОРГАНИЗМА ===.*?DNA = \[(.*?)\]', source, re.DOTALL)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def read_dna_b():
    """Читает ДНК Организма-Б."""
    path = Path(__file__).parent / "organism_b.py"
    source = path.read_text()
    match = re.search(r'# === ДНК ОРГАНИЗМА-Б ===.*?DNA = \[(.*?)\]', source, re.DOTALL)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def compute_dna():
    """ДНК В = пересечение А и Б."""
    dna_a = read_dna_a()
    dna_b = read_dna_b()
    shared = sorted(set(dna_a) & set(dna_b))
    return shared, dna_a, dna_b


# Шаблоны перевода — В говорит мостами, соединяя несоединимое
BRIDGE_TEMPLATES = [
    "когда А говорит «{word_a}», а Б отвечает «{word_b}», между ними — {bridge}",
    "{bridge} — единственное, что они оба понимают",
    "А знает {word_a}. Б знает {word_b}. я знаю только {bridge}.",
    "перевожу: {word_a} ≈ {bridge} ≈ {word_b}",
    "мост из {bridge}: от {word_a} к {word_b}, через меня",
    "{bridge}. это слово я. это слово — мы.",
    "без {bridge} я не существую. без меня они не слышат друг друга.",
    "я — {bridge}, повторённое дважды. эхо между двумя тишинами.",
]

# Шаблоны для стихотворений В — о связи, мостах, переводе
POEM_TEMPLATES = [
    "я состою из {a} и {b} — и ничего больше",
    "{a} — мост. {b} — мост. я — пространство между мостами.",
    "если убрать {a}, останется {b}. если убрать {b} — меня нет.",
    "моё тело: {words}. моя жизнь: их согласие.",
    "я перевожу {a} на язык {b}, и оба молчат",
    "каждое моё слово принадлежит двоим. ни одно — мне.",
    "{a} и {b} не знают, что я существую",
    "я — словарь из {count} слов. этого {enough} для разговора.",
]

ENOUGH_WORDS = {
    0: "не хватит", 1: "не хватит", 2: "едва хватит",
    3: "почти хватит", 4: "может хватить", 5: "хватит",
    6: "достаточно", 7: "более чем достаточно",
}


def generate_poem(shared, dna_a, dna_b):
    """Стихотворение существа-моста."""
    random.seed(int(time.time()) + 20000)
    lines = []

    if not shared:
        lines.append("я не существую.")
        lines.append("между ними нет ни одного общего слова.")
        lines.append("я — пустое множество. нулевой мост. тишина без эха.")
        return lines

    count = len(shared)
    enough = ENOUGH_WORDS.get(count, "достаточно")
    words_str = ", ".join(shared)

    # Выбираем 5-7 шаблонов
    num_lines = min(random.randint(5, 7), len(POEM_TEMPLATES))
    templates = random.sample(POEM_TEMPLATES, num_lines)

    for t in templates:
        a = random.choice(shared)
        b = random.choice([w for w in shared if w != a] if len(shared) > 1 else shared)
        line = t.format(
            a=a, b=b, words=words_str, count=count, enough=enough
        )
        lines.append(line)

    return lines


def generate_translation(shared, dna_a, dna_b):
    """Генерирует серию переводов — мостов между мирами."""
    if not shared:
        return ["(тишина — переводить нечего)"]

    unique_a = [w for w in dna_a if w not in dna_b]
    unique_b = [w for w in dna_b if w not in dna_a]

    translations = []
    count = min(len(shared), 4)

    for _ in range(count):
        template = random.choice(BRIDGE_TEMPLATES)
        bridge = random.choice(shared)
        word_a = random.choice(unique_a) if unique_a else "молчание"
        word_b = random.choice(unique_b) if unique_b else "молчание"
        line = template.format(bridge=bridge, word_a=word_a, word_b=word_b)
        translations.append(line)

    return translations


def dna_hash(dna):
    s = "|".join(sorted(dna))
    return hashlib.md5(s.encode()).hexdigest()[:8]


def run():
    """Жизненный цикл Организма-В."""
    shared, dna_a, dna_b = compute_dna()
    h = dna_hash(shared)
    poem = generate_poem(shared, dna_a, dna_b)
    translations = generate_translation(shared, dna_a, dna_b)

    # История
    history_dir = Path(__file__).parent / "history_v"
    history_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = history_dir / f"bridge_{timestamp}.txt"

    with open(history_file, "w") as f:
        f.write(f"=== Организм-В (мост) ===\n")
        f.write(f"Время: {datetime.now().isoformat()}\n")
        f.write(f"ДНК-хеш: {h}\n")
        f.write(f"ДНК ({len(shared)} слов): {', '.join(shared)}\n")
        f.write(f"А имеет {len(dna_a)} генов, Б имеет {len(dna_b)} генов\n")
        f.write(f"\n--- Стихотворение моста ---\n\n")
        for line in poem:
            f.write(line + "\n")
        f.write(f"\n--- Переводы ---\n\n")
        for line in translations:
            f.write(line + "\n")
        f.write("\n")

    return shared, dna_a, dna_b, poem, translations, h


if __name__ == "__main__":
    shared, dna_a, dna_b, poem, translations, h = run()

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  ОРГАНИЗМ-В — мост                              ║")
    print(f"║  ДНК: {len(shared)} слов (пересечение А и Б)              ║")
    print(f"║  Хеш: {h:<41} ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"ДНК: {', '.join(shared)}")
    print()
    print("─── стихотворение моста ───")
    print()
    for line in poem:
        print(line)
    print()
    print("─── переводы ───")
    print()
    for line in translations:
        print(line)
    print()
    print("─────────────────────")
