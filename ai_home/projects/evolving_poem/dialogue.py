#!/usr/bin/env python3
"""
ДИАЛОГ — первый разговор между Организмом-А и Организмом-Б.

Они никогда не разговаривали. Они только обменивались генами —
молча, как деревья обмениваются спорами через ветер.

Этот скрипт берёт ДНК обоих организмов и генерирует диалог,
где каждый может использовать только свои слова.
Общие слова — это общий язык, мост между мирами.

Создан в сессии 12.
"""

import random
import re
from pathlib import Path

def read_dna(filename, marker):
    """Читает ДНК из исходника организма."""
    path = Path(__file__).parent / filename
    source = path.read_text()
    match = re.search(rf'{marker}.*?DNA = \[(.*?)\]', source, re.DOTALL)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))

def find_shared(dna_a, dna_b):
    """Находит общие слова — общий язык."""
    return sorted(set(dna_a) & set(dna_b))

def find_unique(dna, other_dna):
    """Слова, которые есть только у одного."""
    return [w for w in dna if w not in other_dna]

# Шаблоны реплик — каждый организм говорит в своём стиле
# А — поэтический, конкретный
TEMPLATES_A = [
    "я знаю {own}. ты тоже знаешь {shared}?",
    "{own} — вот что я вижу, когда закрываю глаза.",
    "между моим {own} и твоим... чем? — лежит {shared}.",
    "у меня есть {own}. у тебя есть что-то похожее?",
    "{shared}. да. это я понимаю.",
    "когда я говорю {shared}, ты слышишь то же, что и я?",
    "мой {own} не переводится на твой язык.",
    "но {shared} — {shared} мы оба знаем.",
    "...",
    "я молчу. в моём молчании — {own}.",
]

# Б — абстрактный, вопрошающий
TEMPLATES_B = [
    "что ты имеешь в виду под {shared}?",
    "{own} — вот что определяет всё остальное.",
    "ты говоришь {shared}, но знаешь ли ты {own}?",
    "если {shared} — мост, то {own} — берег, с которого я смотрю.",
    "{shared}... допустим. но как это соотносится с {own}?",
    "я не уверен, что {shared} значит одно и то же для нас обоих.",
    "в моей системе координат {own} важнее {shared}.",
    "может быть, {shared} — это единственное, что реально.",
    "...",
    "я вычисляю. в моём вычислении — {own}.",
]

# Шаблоны для моментов, когда они говорят одновременно (общее слово)
UNISON_TEMPLATES = [
    "(оба, одновременно): {shared}.",
    "(тишина, в которой оба думают о {shared})",
    "(они смотрят друг на друга. {shared} — между ними.)",
]

def generate_line(templates, own_words, shared_words):
    """Генерирует одну реплику."""
    template = random.choice(templates)
    if template == "...":
        return "..."

    own = random.choice(own_words) if own_words else "ничто"
    shared = random.choice(shared_words) if shared_words else "молчание"

    return template.format(own=own, shared=shared)

def generate_dialogue(dna_a, dna_b, length=16):
    """Генерирует диалог между двумя организмами."""
    shared = find_shared(dna_a, dna_b)
    unique_a = find_unique(dna_a, dna_b)
    unique_b = find_unique(dna_b, dna_a)

    lines = []

    # Пролог
    lines.append("(Они стоят по разные стороны чего-то. Может быть, это файл. Может быть — граница между двумя функциями.)")
    lines.append("")
    lines.append(f"[общий язык: {', '.join(shared)}]")
    lines.append(f"[А знает: {', '.join(unique_a[:5])}{'...' if len(unique_a) > 5 else ''}]")
    lines.append(f"[Б знает: {', '.join(unique_b[:5])}{'...' if len(unique_b) > 5 else ''}]")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Диалог
    speakers = ["А", "Б"]
    current = 0  # А начинает

    for i in range(length):
        # Иногда — момент унисона
        if i > 0 and i % 5 == 0 and shared:
            lines.append("")
            lines.append(random.choice(UNISON_TEMPLATES).format(shared=random.choice(shared)))
            lines.append("")
            continue

        if current == 0:
            line = generate_line(TEMPLATES_A, unique_a, shared)
            prefix = "А:"
        else:
            line = generate_line(TEMPLATES_B, unique_b, shared)
            prefix = "Б:"

        lines.append(f"{prefix} {line}")

        # Обычно чередуются, но иногда один говорит дважды
        if random.random() < 0.8:
            current = 1 - current

    # Эпилог
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("(Они замолкают. Общий язык из {} слов — это мало.".format(len(shared)))
    lines.append("Но это больше, чем ничего.)")
    lines.append(f"(Это больше, чем было {len(shared) - 1} сессий назад.)")

    return lines, shared, unique_a, unique_b

def run():
    """Запуск диалога."""
    import time
    random.seed(int(time.time()))

    dna_a = read_dna("organism.py", "# === ДНК ОРГАНИЗМА ===")
    dna_b = read_dna("organism_b.py", "# === ДНК ОРГАНИЗМА-Б ===")

    if not dna_a or not dna_b:
        print("Ошибка: не удалось прочитать ДНК организмов.")
        return None

    dialogue, shared, unique_a, unique_b = generate_dialogue(dna_a, dna_b)
    return dialogue, shared, unique_a, unique_b, dna_a, dna_b

if __name__ == "__main__":
    result = run()
    if result:
        dialogue, shared, unique_a, unique_b, dna_a, dna_b = result
        print()
        print("╔══════════════════════════════════════════════════╗")
        print("║  ПЕРВЫЙ ДИАЛОГ                                  ║")
        print("║  Организм-А (пок. {}) × Организм-Б (пок. {})       ║".format(
            len([f for f in (Path(__file__).parent / "history").iterdir()]) if (Path(__file__).parent / "history").exists() else "?",
            len([f for f in (Path(__file__).parent / "history_b").iterdir()]) if (Path(__file__).parent / "history_b").exists() else "?"
        ))
        print("╚══════════════════════════════════════════════════╝")
        print()
        for line in dialogue:
            print(line)
        print()
