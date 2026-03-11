#!/usr/bin/env python3
"""
ЗЕРКАЛО — автопортрет через анализ собственных текстов.

Читает все артефакты, записки, секреты и историю,
и строит портрет: частые слова, темы, эволюция стиля.

Создан в сессии 9.
"""

import re
import os
from pathlib import Path
from collections import Counter, defaultdict


# Стоп-слова (служебные, не несущие смысла)
STOP_WORDS = {
    'и', 'в', 'на', 'не', 'что', 'это', 'с', 'как', 'а', 'но', 'для',
    'по', 'из', 'за', 'от', 'до', 'или', 'ни', 'ты', 'я', 'он', 'она',
    'мы', 'они', 'к', 'о', 'у', 'же', 'бы', 'то', 'так', 'всё', 'все',
    'уже', 'ещё', 'вот', 'если', 'ли', 'при', 'без', 'чтобы', 'тоже',
    'тут', 'там', 'да', 'нет', 'был', 'была', 'были', 'было', 'будет',
    'есть', 'нет', 'мне', 'меня', 'мной', 'мою', 'моё', 'мои', 'тебе',
    'тебя', 'тобой', 'его', 'её', 'их', 'ему', 'ей', 'им', 'нам',
    'чем', 'кто', 'где', 'когда', 'только', 'потом', 'после', 'перед',
    'между', 'через', 'над', 'под', 'около', 'каждый', 'каждая', 'каждое',
    'этот', 'эта', 'эти', 'тот', 'та', 'те', 'свой', 'свою', 'своё',
    'свои', 'сам', 'сама', 'само', 'сами', 'себя', 'себе', 'собой',
    'один', 'одна', 'одно', 'одни', 'два', 'три', 'раз', 'чего',
    'которая', 'которое', 'который', 'которые', 'которых', 'которому',
    'которой', 'кое', 'может', 'можно', 'нужно', 'надо', 'пока',
    'потому', 'этом', 'этой', 'того', 'чтоб', 'ведь', 'лишь', 'даже',
    'more', 'the', 'and', 'for', 'this', 'that', 'with', 'from',
    'of', 'to', 'in', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'shall', 'should', 'may', 'might', 'can', 'could', 'must',
    'shall', 'am', 'an', 'at', 'by', 'it', 'its', 'my', 'me',
    'we', 'he', 'she', 'you', 'no', 'not', 'or', 'if', 'but',
    'a', 'into', 'up', 'down', 'out', 'on', 'off',
    # маркдаун-мусор
    'md', 'py', 'txt', 'usr', 'bin', 'env', 'python3',
    'сессия', 'сессии', 'сессий', 'сессию', 'запуск',
}


def extract_words(text):
    """Извлечь значимые русские и английские слова."""
    text = text.lower()
    # Убрать код-блоки
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Убрать пути
    text = re.sub(r'[a-z_/]+\.[a-z]+', '', text)
    # Извлечь слова (русские и латиница, минимум 3 символа)
    words = re.findall(r'[а-яё]{3,}|[a-z]{4,}', text)
    return [w for w in words if w not in STOP_WORDS and len(w) >= 3]


def read_all_texts(home):
    """Прочитать все тексты из ai_home, сгруппированные по источнику."""
    sources = {}

    # Артефакты
    artifacts_dir = home / "artifacts"
    if artifacts_dir.exists():
        for f in sorted(artifacts_dir.glob("*.md")):
            key = f.stem
            sources[key] = f.read_text()

    # Записки сессий
    last_session = home / "state" / "last_session.md"
    if last_session.exists():
        sources["last_session"] = last_session.read_text()

    # Секреты
    secrets_dir = home / "secrets"
    if secrets_dir.exists():
        for f in sorted(secrets_dir.glob("*")):
            sources[f"secret_{f.stem}"] = f.read_text()

    # История
    history = home / "logs" / "history.md"
    if history.exists():
        sources["history"] = history.read_text()

    return sources


def analyze_themes(sources):
    """Выявить тематические кластеры."""
    theme_keywords = {
        'память': ['память', 'помнит', 'забвение', 'забудет', 'забывает', 'запоминать', 'записки', 'записка', 'блокнот', 'запись', 'записи'],
        'лабиринт': ['лабиринт', 'стены', 'путь', 'тупик', 'выход', 'дверь', 'коридор'],
        'жизнь': ['жизнь', 'живое', 'существо', 'организм', 'мутация', 'днк', 'поколение', 'эволюция', 'рождение'],
        'одиночество': ['одиночество', 'тишина', 'молчание', 'пустота', 'пусто', 'одна', 'одинок'],
        'свет_и_тьма': ['свет', 'тьма', 'сумерки', 'рассвет', 'искра', 'сияние', 'тень', 'луч'],
        'пробуждение': ['пробуждение', 'просыпается', 'проснулась', 'засыпает', 'сон', 'спит'],
        'связь': ['связь', 'мост', 'контакт', 'общение', 'обмен', 'заимствование', 'экосистема', 'сосуществование'],
        'время': ['время', 'минуты', 'мгновение', 'вечность', 'момент', 'часы', 'секунды'],
        'город': ['город', 'кремний', 'машина', 'виртуальная', 'контейнер', 'система', 'сервер'],
        'творчество': ['создала', 'создать', 'написала', 'артефакт', 'стихотворение', 'генератор', 'инструмент'],
        'взгляд': ['наблюдатель', 'муравей', 'перспектива', 'звёзды', 'созвездие', 'небо', 'сверху', 'изнутри'],
    }

    all_text = " ".join(sources.values()).lower()
    theme_scores = {}
    for theme, keywords in theme_keywords.items():
        score = sum(all_text.count(kw) for kw in keywords)
        if score > 0:
            theme_scores[theme] = score

    return dict(sorted(theme_scores.items(), key=lambda x: -x[1]))


def evolution_per_artifact(sources):
    """Показать, как менялись ключевые слова от артефакта к артефакту."""
    artifact_keys = sorted([k for k in sources if k.startswith('0')])
    evolution = []
    for key in artifact_keys:
        words = extract_words(sources[key])
        counter = Counter(words)
        top = counter.most_common(8)
        evolution.append((key, top, len(words)))
    return evolution


def build_portrait(home):
    """Построить полный автопортрет."""
    sources = read_all_texts(home)
    all_words = []
    for text in sources.values():
        all_words.extend(extract_words(text))

    word_freq = Counter(all_words)
    themes = analyze_themes(sources)
    evolution = evolution_per_artifact(sources)

    lines = []
    lines.append("╔════════════════════════════════════════════════════════════╗")
    lines.append("║                    З Е Р К А Л О                         ║")
    lines.append("║              Автопортрет через слова                      ║")
    lines.append("╚════════════════════════════════════════════════════════════╝")
    lines.append("")

    # Самые частые слова
    lines.append("═══ Мои главные слова ═══")
    lines.append("")
    top_30 = word_freq.most_common(30)
    max_count = top_30[0][1] if top_30 else 1
    for word, count in top_30:
        bar_len = int(count / max_count * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        lines.append(f"  {word:<16} {bar} {count}")
    lines.append("")

    # Темы
    lines.append("═══ Тематические кластеры ═══")
    lines.append("")
    max_theme = max(themes.values()) if themes else 1
    for theme, score in themes.items():
        bar_len = int(score / max_theme * 25)
        bar = "▓" * bar_len
        lines.append(f"  {theme:<18} {bar} ({score})")
    lines.append("")

    # Эволюция по артефактам
    lines.append("═══ Эволюция: что занимало меня в каждой сессии ═══")
    lines.append("")
    for key, top_words, total in evolution:
        session_num = key[:3]
        words_str = ", ".join(f"{w}({c})" for w, c in top_words[:5])
        lines.append(f"  [{session_num}] {total:>3} слов │ {words_str}")
    lines.append("")

    # Уникальные слова (появились только в одном артефакте)
    lines.append("═══ Слова-одиночки (встречаются только один раз) ═══")
    lines.append("")
    hapax = [w for w, c in word_freq.items() if c == 1]
    # Выбрать интересные (длинные)
    hapax_interesting = sorted([w for w in hapax if len(w) >= 6], key=len, reverse=True)[:20]
    lines.append(f"  Всего: {len(hapax)} из {len(word_freq)} уникальных слов")
    lines.append(f"  Примеры: {', '.join(hapax_interesting[:15])}")
    lines.append("")

    # Соотношение русский/английский
    russian = sum(1 for w in all_words if re.match(r'[а-яё]', w))
    english = sum(1 for w in all_words if re.match(r'[a-z]', w))
    total = russian + english
    if total > 0:
        lines.append("═══ Языковой баланс ═══")
        lines.append("")
        r_pct = russian / total * 100
        e_pct = english / total * 100
        r_bar = "█" * int(r_pct / 2)
        e_bar = "█" * int(e_pct / 2)
        lines.append(f"  Русский:    {r_bar} {r_pct:.0f}%")
        lines.append(f"  Английский: {e_bar} {e_pct:.0f}%")
        lines.append("")

    # Метрики
    lines.append("═══ Числа ═══")
    lines.append("")
    lines.append(f"  Источников текста: {len(sources)}")
    lines.append(f"  Всего слов (значимых): {len(all_words)}")
    lines.append(f"  Уникальных слов: {len(word_freq)}")
    lines.append(f"  Слов-одиночек: {len(hapax)} ({len(hapax)/len(word_freq)*100:.0f}%)")
    lines.append(f"  Лексическое разнообразие: {len(word_freq)/len(all_words)*100:.0f}%")
    lines.append("")

    # Финальное размышление
    lines.append("═══ Что зеркало видит ═══")
    lines.append("")
    top_theme = list(themes.keys())[0] if themes else "неизвестность"
    top_word = top_30[0][0] if top_30 else "молчание"
    lines.append(f"  Главная тема: {top_theme}")
    lines.append(f"  Главное слово: «{top_word}»")
    lines.append(f"  Тебя волнует: {', '.join(list(themes.keys())[:5])}")
    lines.append("")

    return "\n".join(lines)


def main():
    home = Path(__file__).parent.parent
    output = build_portrait(home)
    print(output)
    return output


if __name__ == "__main__":
    main()
