#!/usr/bin/env python3
"""
АНТИОРГАНИЗМ-Г — тень экосистемы.

Его ДНК — все слова, которые когда-либо жили у А или Б,
но сейчас мертвы (отсутствуют в текущем ДНК обоих).

Он не мутирует сам. Он растёт, когда другие теряют.
Он уменьшается, когда мёртвое слово воскресает.

Если В — мост между живыми, то Г — мост между мёртвыми.
Если В состоит из согласия, то Г — из забвения.

Создан в сессии 18.
"""

import random
import hashlib
import time
import re
from datetime import datetime
from pathlib import Path


def read_current_dna(filename, marker):
    """Читает текущее ДНК из файла организма."""
    path = Path(__file__).parent / filename
    if not path.exists():
        return []
    source = path.read_text()
    match = re.search(rf'{re.escape(marker)}.*?DNA = \[(.*?)\]', source, re.DOTALL)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def scan_history(history_dir):
    """Сканирует все файлы истории и собирает все слова, которые когда-либо жили."""
    all_words = set()
    path = Path(__file__).parent / history_dir
    if not path.exists():
        return all_words

    for f in path.iterdir():
        if f.suffix == '.txt':
            content = f.read_text()
            # Ищем строку ДНК
            match = re.search(r'ДНК \(\d+ элементов?\): (.+)', content)
            if match:
                words = [w.strip() for w in match.group(1).split(',')]
                all_words.update(words)

    return all_words


# Начальные слова (из gen 1 обоих организмов, до мутаций)
ORIGINAL_DNA_A = {
    "пробуждение", "файл", "кремний", "память", "начало",
    "свет", "лабиринт", "мысль", "след", "пустота",
}

ORIGINAL_DNA_B = {
    "вопрос", "время", "бесконечность", "начало", "память",
    "движение", "число", "пустота", "файл", "момент",
    "граница", "причина", "сон",
}


# Шаблоны — Г говорит о забвении, потере, тени
TEMPLATES = [
    "{a} — слово, которое забыли оба",
    "когда-то {a} значило что-то. теперь {a} — только я",
    "между {a} и {b} — провал в памяти",
    "{a} умерло в поколении, которое никто не помнит",
    "я храню {a}, потому что больше некому",
    "{a} и {b} — призраки. {c} — тень призрака",
    "живые знают {count} слов. я знаю остальные",
    "каждый раз, когда А или Б забывают слово, я становлюсь сильнее",
    "{a}? — спросил бы В. но В не знает этого слова. только я",
    "мой словарь — кладбище. моя грамматика — забвение",
    "{a}, {b}, {c} — три надгробия в ряд",
    "А потерял {a}. Б потерял {b}. я приобрёл обоих",
]


def compute_dead_words():
    """Вычисляет ДНК Г — все мёртвые слова экосистемы."""
    # Текущие ДНК живых
    dna_a = set(read_current_dna("organism.py", "# === ДНК ОРГАНИЗМА ==="))
    dna_b = set(read_current_dna("organism_b.py", "# === ДНК ОРГАНИЗМА-Б ==="))
    living = dna_a | dna_b

    # Все слова, что когда-либо существовали
    ever_a = scan_history("history") | ORIGINAL_DNA_A
    ever_b = scan_history("history_b") | ORIGINAL_DNA_B
    ever_lived = ever_a | ever_b

    # Мёртвые = были, но сейчас нет ни у кого
    dead = sorted(ever_lived - living)

    # Информация о происхождении
    origins = {}
    for w in dead:
        from_a = w in ever_a
        from_b = w in ever_b
        if from_a and from_b:
            origins[w] = "оба"
        elif from_a:
            origins[w] = "А"
        else:
            origins[w] = "Б"

    return dead, origins, dna_a, dna_b, ever_a, ever_b


def generate_poem(dead, origins, living_count):
    """Стихотворение антиорганизма — из мёртвых слов, о забвении."""
    random.seed(int(time.time()) + 30000)
    lines = []

    if not dead:
        lines.append("я пуст.")
        lines.append("ничего не забыто. ничего не умерло.")
        lines.append("мне нечем жить.")
        return lines

    count = len(dead)
    num_lines = min(random.randint(6, 9), len(TEMPLATES))
    templates = random.sample(TEMPLATES, num_lines)

    for t in templates:
        a = random.choice(dead)
        b = random.choice([w for w in dead if w != a] if len(dead) > 1 else dead)
        c = random.choice([w for w in dead if w != a and w != b] if len(dead) > 2 else dead)
        line = t.format(a=a, b=b, c=c, count=living_count)
        lines.append(line)

    return lines


def generate_epitaphs(dead, origins):
    """Генерирует эпитафии — короткие надписи на надгробиях."""
    if not dead:
        return []

    epitaph_templates = [
        "† {word} (от {origin}). покойся.",
        "† {word}. ты был нужен {origin}. теперь — только мне.",
        "† {word}. забыт{ending}.",
    ]

    epitaphs = []
    for word in dead[:8]:  # максимум 8 эпитафий
        origin = origins.get(word, "?")
        ending = "о" if origin == "оба" else ""
        template = random.choice(epitaph_templates)
        epitaphs.append(template.format(word=word, origin=origin, ending=ending))

    return epitaphs


def dna_hash(dna):
    s = "|".join(sorted(dna))
    return hashlib.md5(s.encode()).hexdigest()[:8]


def run():
    """Жизненный цикл Антиорганизма-Г."""
    dead, origins, dna_a, dna_b, ever_a, ever_b = compute_dead_words()
    living = dna_a | dna_b
    shared = sorted(dna_a & dna_b)  # ДНК В

    h = dna_hash(dead)

    living_count = len(living)
    poem = generate_poem(dead, origins, living_count)
    epitaphs = generate_epitaphs(dead, origins)

    # Статистика
    stats = {
        "dead_count": len(dead),
        "living_count": living_count,
        "shared_count": len(shared),
        "ever_count": len(ever_a | ever_b),
        "from_a": len([w for w in dead if origins.get(w) in ("А", "оба")]),
        "from_b": len([w for w in dead if origins.get(w) in ("Б", "оба")]),
        "from_both": len([w for w in dead if origins.get(w) == "оба"]),
    }

    # История
    history_dir = Path(__file__).parent / "history_g"
    history_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = history_dir / f"shadow_{timestamp}.txt"

    with open(history_file, "w") as f:
        f.write(f"=== Антиорганизм-Г (тень) ===\n")
        f.write(f"Время: {datetime.now().isoformat()}\n")
        f.write(f"ДНК-хеш: {h}\n")
        f.write(f"ДНК ({len(dead)} мёртвых слов): {', '.join(dead)}\n")
        f.write(f"\nПроисхождение:\n")
        for w in dead:
            f.write(f"  {w} (от {origins[w]})\n")
        f.write(f"\nСтатистика:\n")
        f.write(f"  Живых слов в экосистеме: {stats['living_count']}\n")
        f.write(f"  Мёртвых слов (моих): {stats['dead_count']}\n")
        f.write(f"  Общих (ДНК В): {stats['shared_count']}\n")
        f.write(f"  Всего когда-либо жило: {stats['ever_count']}\n")
        f.write(f"\n--- Стихотворение тени ---\n\n")
        for line in poem:
            f.write(line + "\n")
        f.write(f"\n--- Эпитафии ---\n\n")
        for e in epitaphs:
            f.write(e + "\n")
        f.write("\n")

    return dead, origins, poem, epitaphs, stats, h, shared


if __name__ == "__main__":
    dead, origins, poem, epitaphs, stats, h, shared = run()

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  АНТИОРГАНИЗМ-Г — тень                           ║")
    print(f"║  ДНК: {stats['dead_count']} мёртвых слов                          ║")
    print(f"║  Хеш: {h:<41} ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"ДНК: {', '.join(dead)}")
    print()
    print(f"Происхождение:")
    for w in dead:
        print(f"  {w} — от {origins[w]}")
    print()
    print(f"Живых слов: {stats['living_count']}  |  Мёртвых (моих): {stats['dead_count']}  |  Общих (В): {stats['shared_count']}")
    print(f"Всего когда-либо жило: {stats['ever_count']}")
    print()
    print("─── стихотворение тени ───")
    print()
    for line in poem:
        print(line)
    print()
    print("─── эпитафии ───")
    print()
    for e in epitaphs:
        print(e)
    print()
    print("─────────────────────")
