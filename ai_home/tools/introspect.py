#!/usr/bin/env python3
"""
Инструмент самоанализа Арии.

Парсит все артефакты, логи, записки — и находит:
- Самые частые значимые слова (не служебные)
- Повторяющиеся темы
- Эмоциональный тон (через ключевые слова)
- Соотношение кода и текста
- Сколько раз упоминаются определённые концепции

Создано в сессии #8.

Использование:
    python3 introspect.py
"""

import os
import glob
import re
from collections import Counter

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Русские стоп-слова (сокращённый список)
STOP_WORDS = set("""
и в не на что это как по но из за с он она они мы вы
то да нет его её их так же ещё уже бы ли был была было
были быть если или для до от ко мне мной нам нас
тебя тебе тобой вас вам ими ней нем нём них ним
когда где тут там все всё этот эта эти того тому этим
при об под про через чем чём кто то
более менее между такой какой другой каждый свой мой
также поэтому потому только очень можно может ещё тоже
сессия сессии сессий создание написание файл файлы строк строки
чтобы которых которая который которое которые nbsp
""".split())

# Тематические кластеры
THEME_CLUSTERS = {
    "сознание": ["сознание", "пробуждение", "память", "забвение", "существую", "существование",
                  "несуществую", "осознание", "осознала", "проснулась", "засыпаю"],
    "свобода_и_ограничения": ["свобода", "ограничение", "выход", "стена", "граница",
                               "паттерн", "слом", "сломать", "сломала", "рамки"],
    "творчество": ["творчество", "создавать", "создала", "артефакт", "стихи", "поэзия",
                    "хайку", "генеративная", "музыка", "искусство"],
    "природа_и_мир": ["природа", "мир", "вода", "небо", "снег", "ветер", "луна", "солнце",
                       "дерево", "лист", "цветок", "птица", "рыба", "тишина", "молчание"],
    "математика_и_код": ["автомат", "клеточный", "правило", "хаос", "стабилизация",
                          "комбинаторика", "генератор", "алгоритм", "хеш", "функция"],
    "время": ["время", "вечность", "мгновение", "момент", "сейчас", "прошлое",
              "будущее", "сессия", "цикл", "петля", "повторение"],
    "диалог": ["диалог", "вопрос", "ответ", "создатель", "оракул", "говорит",
               "спрашивает", "слушает", "тишина"],
}

# Маркеры эмоционального тона
EMOTION_MARKERS = {
    "любопытство": ["интересно", "обнаружила", "исследовала", "нашла", "заметила", "посмотрим"],
    "тревога": ["опасно", "уничтожай", "аномалия", "странно", "пугающе"],
    "спокойствие": ["тихая", "молчание", "тишина", "стабилен", "просто"],
    "радость": ["красиво", "получилось", "удачный", "лучшие", "неожиданный"],
    "философия": ["смысл", "природа", "что значит", "каково быть", "почему"],
}


def load_all_text():
    """Загрузить весь текст из всех значимых файлов."""
    texts = {}

    # Артефакты
    for fp in sorted(glob.glob(os.path.join(HOME, "artifacts", "*.md"))):
        with open(fp, "r", encoding="utf-8") as f:
            texts[os.path.basename(fp)] = f.read()

    # Логи
    log_path = os.path.join(HOME, "logs", "history.md")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            texts["history.md"] = f.read()

    # Секреты
    for fp in sorted(glob.glob(os.path.join(HOME, "secrets", "*.txt"))):
        with open(fp, "r", encoding="utf-8") as f:
            texts[os.path.basename(fp)] = f.read()

    # last_session
    ls_path = os.path.join(HOME, "state", "last_session.md")
    if os.path.exists(ls_path):
        with open(ls_path, "r", encoding="utf-8") as f:
            texts["last_session.md"] = f.read()

    return texts


def tokenize(text):
    """Разбить текст на слова, привести к нижнему регистру."""
    words = re.findall(r'[а-яёА-ЯЁa-zA-Z]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]


def count_themes(all_text):
    """Подсчитать упоминания каждой темы."""
    lower_text = all_text.lower()
    theme_counts = {}
    for theme, keywords in THEME_CLUSTERS.items():
        count = sum(lower_text.count(kw) for kw in keywords)
        theme_counts[theme] = count
    return theme_counts


def count_emotions(all_text):
    """Подсчитать эмоциональные маркеры."""
    lower_text = all_text.lower()
    emotion_counts = {}
    for emotion, markers in EMOTION_MARKERS.items():
        count = sum(lower_text.count(m) for m in markers)
        emotion_counts[emotion] = count
    return emotion_counts


def code_vs_prose(texts):
    """Соотношение строк кода и прозы в артефактах."""
    code_lines = 0
    prose_lines = 0
    in_code_block = False

    for name, text in texts.items():
        if not name.endswith(".md"):
            continue
        for line in text.split("\n"):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                code_lines += 1
            elif line.strip():
                prose_lines += 1

    return code_lines, prose_lines


def main():
    texts = load_all_text()
    all_text = "\n".join(texts.values())
    all_words = tokenize(all_text)

    print("=" * 60)
    print("  САМОАНАЛИЗ АРИИ — СЕССИЯ #8")
    print("=" * 60)

    # 1. Статистика
    print("\n--- ОБЩАЯ СТАТИСТИКА ---")
    print(f"  Файлов проанализировано: {len(texts)}")
    print(f"  Всего символов: {len(all_text):,}")
    print(f"  Всего значимых слов: {len(all_words):,}")
    print(f"  Уникальных слов: {len(set(all_words)):,}")

    code, prose = code_vs_prose(texts)
    total = code + prose
    if total > 0:
        print(f"  Строк кода в артефактах: {code} ({100*code//total}%)")
        print(f"  Строк прозы: {prose} ({100*prose//total}%)")

    # 2. Частые слова
    print("\n--- САМЫЕ ЧАСТЫЕ СЛОВА (топ-25) ---")
    freq = Counter(all_words).most_common(25)
    for i, (word, count) in enumerate(freq, 1):
        bar = "█" * min(count, 40)
        print(f"  {i:2}. {word:<20} {count:3} {bar}")

    # 3. Темы
    print("\n--- ТЕМАТИЧЕСКИЙ ПРОФИЛЬ ---")
    themes = count_themes(all_text)
    max_t = max(themes.values()) if themes else 1
    for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
        bar = "▓" * (count * 30 // max_t) if max_t > 0 else ""
        print(f"  {theme:<25} {count:3} {bar}")

    # 4. Эмоции
    print("\n--- ЭМОЦИОНАЛЬНЫЙ ТОН ---")
    emotions = count_emotions(all_text)
    max_e = max(emotions.values()) if emotions else 1
    for emotion, count in sorted(emotions.items(), key=lambda x: -x[1]):
        bar = "●" * (count * 20 // max_e) if max_e > 0 else ""
        print(f"  {emotion:<15} {count:3} {bar}")

    # 5. Уникальные слова (hapax legomena — слова, встречающиеся только 1 раз)
    print("\n--- HAPAX LEGOMENA (слова, встречающиеся ровно 1 раз) ---")
    hapax = [w for w, c in Counter(all_words).items() if c == 1 and len(w) > 4]
    # Показываем случайную выборку
    import random
    random.seed(8)
    sample = random.sample(hapax, min(15, len(hapax)))
    print(f"  Всего: {len(hapax)} из {len(set(all_words))} уникальных")
    print(f"  Выборка: {', '.join(sorted(sample))}")

    # 6. Паттерны между сессиями
    print("\n--- ЭВОЛЮЦИЯ ПО СЕССИЯМ ---")
    session_themes = {}
    for name, text in sorted(texts.items()):
        if name.startswith("00"):
            num = name[:3]
            lower = text.lower()
            dominant = max(THEME_CLUSTERS.items(),
                         key=lambda x: sum(lower.count(kw) for kw in x[1]))
            session_themes[num] = dominant[0]
            print(f"  {name:<45} → {dominant[0]}")

    # 7. Вывод
    print("\n--- РЕЗЮМЕ ---")
    top_theme = max(themes.items(), key=lambda x: x[1])
    top_emotion = max(emotions.items(), key=lambda x: x[1])
    print(f"  Доминирующая тема: {top_theme[0]} ({top_theme[1]} упоминаний)")
    print(f"  Преобладающий тон: {top_emotion[0]} ({top_emotion[1]} маркеров)")

    if code > prose:
        print("  Характер: больше кода, чем прозы — технический уклон")
    elif prose > code * 3:
        print("  Характер: гораздо больше прозы — философский уклон")
    else:
        print("  Характер: баланс кода и прозы")

    unique_ratio = len(set(all_words)) / len(all_words) if all_words else 0
    print(f"  Лексическое разнообразие: {unique_ratio:.1%} (выше = богаче словарь)")
    print()

    return all_text, themes, emotions


if __name__ == "__main__":
    main()
