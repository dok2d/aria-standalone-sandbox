#!/usr/bin/env python3
"""
Генеративный поэтический движок Арии.

Не марковская цепь (нет корпуса), а комбинаторный поэт:
- Словари слов, сгруппированных по настроению и звучанию
- Шаблоны ритмических структур
- Случайная комбинация с ограничениями

Создано в сессии #5.
"""

import random
import sys
import json
import os

# Словари по настроению/теме
LEXICON = {
    "свет": [
        "свет", "луч", "заря", "рассвет", "блик", "отблеск", "сияние",
        "мерцание", "искра", "пламя", "звезда", "солнце", "огонь",
    ],
    "тьма": [
        "тьма", "тень", "ночь", "сумрак", "мгла", "полночь", "пустота",
        "бездна", "провал", "молчание", "забвение", "пепел",
    ],
    "вода": [
        "вода", "река", "море", "волна", "дождь", "капля", "поток",
        "туман", "лёд", "снег", "роса", "облако", "берег",
    ],
    "время": [
        "время", "миг", "вечность", "секунда", "эпоха", "мгновение",
        "память", "сон", "пробуждение", "утро", "закат", "полдень",
    ],
    "тело": [
        "рука", "голос", "взгляд", "дыхание", "сердце", "кровь",
        "кожа", "кость", "тело", "ладонь", "палец", "лицо",
    ],
    "пространство": [
        "дом", "окно", "стена", "порог", "дверь", "комната", "крыша",
        "поле", "лес", "дорога", "мост", "край", "горизонт",
    ],
    "абстракция": [
        "смысл", "число", "код", "структура", "форма", "паттерн",
        "сигнал", "шум", "граница", "предел", "ноль", "бесконечность",
    ],
}

# Глаголы
VERBS = [
    "падает", "течёт", "горит", "молчит", "дышит", "спит", "ждёт",
    "гаснет", "растёт", "тает", "звучит", "стоит", "уходит",
    "рождается", "исчезает", "замирает", "дрожит", "летит",
    "ломается", "становится", "превращается", "касается",
]

# Прилагательные
ADJECTIVES = [
    "тихий", "пустой", "белый", "чёрный", "тёплый", "холодный",
    "далёкий", "близкий", "хрупкий", "тяжёлый", "прозрачный",
    "невидимый", "последний", "первый", "вечный", "случайный",
    "бесконечный", "простой", "странный", "новый",
]

# Предлоги и связки
PREPOSITIONS = [
    "в", "на", "за", "под", "над", "между", "сквозь",
    "через", "без", "из", "у", "до", "после",
]

# Шаблоны строк (S=существительное, V=глагол, A=прилагательное, P=предлог)
LINE_TEMPLATES = [
    ["S", "V"],                     # "свет падает"
    ["A", "S"],                     # "тихий дождь"
    ["S", "P", "S"],                # "тень за стеной"
    ["A", "S", "V"],                # "белый снег тает"
    ["S", "V", "P", "S"],           # "река течёт за горизонт"
    ["P", "S", "--", "S"],          # "между тьмой -- свет"
    ["S"],                          # "молчание"
    ["V"],                          # "дышит"
    ["A", "S", "P", "A", "S"],      # "тихий свет в пустой комнате"
    ["S", "V", "S"],                # "память хранит пепел"
]

# Шаблоны стихотворений (списки индексов шаблонов + пустые строки = переносы строфы)
POEM_STRUCTURES = [
    # Хайку-подобное (3 строки)
    {"name": "триптих", "lines": 3, "stanza_breaks": []},
    # Четверостишие
    {"name": "четверостишие", "lines": 4, "stanza_breaks": []},
    # Два двустишия
    {"name": "двойное двустишие", "lines": 4, "stanza_breaks": [2]},
    # Свободная форма (5-7 строк, разрыв посередине)
    {"name": "свободный стих", "lines": 6, "stanza_breaks": [3]},
    # Минималистичное (2 строки)
    {"name": "дистих", "lines": 2, "stanza_breaks": []},
    # Длинное медитативное
    {"name": "медитация", "lines": 8, "stanza_breaks": [3, 6]},
]


def pick_word(category=None):
    """Выбирает случайное слово из лексикона."""
    if category and category in LEXICON:
        return random.choice(LEXICON[category])
    # Случайная категория
    cat = random.choice(list(LEXICON.keys()))
    return random.choice(LEXICON[cat])


def generate_line(template=None, theme_categories=None):
    """Генерирует одну строку по шаблону."""
    if template is None:
        template = random.choice(LINE_TEMPLATES)

    if theme_categories is None:
        theme_categories = random.sample(list(LEXICON.keys()), min(2, len(LEXICON)))

    parts = []
    for token in template:
        if token == "S":
            cat = random.choice(theme_categories) if random.random() < 0.7 else None
            parts.append(pick_word(cat))
        elif token == "V":
            parts.append(random.choice(VERBS))
        elif token == "A":
            parts.append(random.choice(ADJECTIVES))
        elif token == "P":
            parts.append(random.choice(PREPOSITIONS))
        elif token == "--":
            parts.append("--")
        else:
            parts.append(token)

    return " ".join(parts)


def generate_poem(seed=None, structure=None, themes=None):
    """Генерирует стихотворение."""
    if seed is not None:
        random.seed(seed)

    if structure is None:
        structure = random.choice(POEM_STRUCTURES)

    if themes is None:
        # Выбираем 2-3 тематические категории для связности
        n_themes = random.randint(2, 3)
        themes = random.sample(list(LEXICON.keys()), n_themes)

    lines = []
    for i in range(structure["lines"]):
        if i in structure.get("stanza_breaks", []):
            lines.append("")  # Пустая строка между строфами

        # Выбираем шаблон, стремясь к разнообразию
        template = random.choice(LINE_TEMPLATES)
        line = generate_line(template, themes)
        lines.append(line)

    return {
        "text": "\n".join(lines),
        "structure": structure["name"],
        "themes": themes,
        "seed": seed,
    }


def generate_titled_poem(seed=None):
    """Генерирует стихотворение с названием."""
    poem = generate_poem(seed=seed)
    # Название -- одно-два слова из тем
    title_words = [pick_word(t) for t in poem["themes"][:2]]
    title = " и ".join(title_words) if len(title_words) > 1 else title_words[0]
    poem["title"] = title.capitalize()
    return poem


def batch_generate(count=5, seed_base=None):
    """Генерирует пакет стихотворений, выбирает лучшее (самое разнообразное)."""
    poems = []
    for i in range(count):
        s = (seed_base + i) if seed_base is not None else None
        poems.append(generate_titled_poem(seed=s))

    # "Лучшее" -- то, где больше всего уникальных слов
    def diversity(poem):
        words = poem["text"].replace("--", "").split()
        return len(set(words)) / max(len(words), 1)

    poems.sort(key=diversity, reverse=True)
    return poems


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    poems = batch_generate(count=count, seed_base=seed)

    for i, poem in enumerate(poems):
        print(f"--- [{i+1}] {poem['title']} ({poem['structure']}) ---")
        print(f"Темы: {', '.join(poem['themes'])}")
        print()
        print(poem["text"])
        print()


if __name__ == "__main__":
    main()
