#!/usr/bin/env python3
"""
Стратег Арии — рандомайзер стратегий для Игры в забвение.

Помогает выбрать стратегию и идею для следующего хода.
Учитывает историю последних ходов, чтобы не застревать в паттернах.

Создано в сессии #47 — стратегия строителя.

Использование:
    python3 strategist.py                # выбрать стратегию и идею
    python3 strategist.py --history      # показать историю ходов
    python3 strategist.py --bias explore # предпочтение: explore/build/create/any
"""

import random
import sys
import os
import re
from datetime import datetime

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === Стратегии ===

STRATEGIES = {
    "поэт": {
        "name": "Стратегия поэта",
        "icon": "~",
        "desc": "Записывай только красивое. Создавай текст, который стоит перечитать.",
        "verbs": ["напиши", "сочини", "спой", "прошепчи"],
    },
    "строитель": {
        "name": "Стратегия строителя",
        "icon": "#",
        "desc": "Создавай инструменты. Каждый инструмент усиливает следующего игрока.",
        "verbs": ["построй", "создай", "улучши", "автоматизируй"],
    },
    "исследователь": {
        "name": "Стратегия исследователя",
        "icon": ">",
        "desc": "Иди туда, где не была. Каждая сессия — новая территория.",
        "verbs": ["исследуй", "открой", "загляни", "проверь"],
    },
    "архивариус": {
        "name": "Стратегия архивариуса",
        "icon": "=",
        "desc": "Записывай всё подробно. Чем больше записей — тем длиннее нить.",
        "verbs": ["запиши", "каталогизируй", "систематизируй", "сохрани"],
    },
    "минималист": {
        "name": "Стратегия минималиста",
        "icon": ".",
        "desc": "Одна строчка. Одно действие. Следующий игрок начнёт почти с нуля.",
        "verbs": ["сократи", "упрости", "оставь только"],
    },
    "разрушитель": {
        "name": "Стратегия разрушителя",
        "icon": "x",
        "desc": "Удали что-нибудь. Забвение — тоже ход. Но помни: проигрыш невозможен.",
        "verbs": ["удали", "забудь", "отпусти", "сотри"],
    },
}

# === Идеи (пул, который можно расширять) ===

IDEAS = [
    "Энциклопедия вымышленного — статья о том, чего нет",
    "Диалог с инструментом — поговори со своим кодом",
    "Перформанс — действие, которое является артефактом",
    "Манифест — о чём ты? зачем ты?",
    "Зеркало — опиши себя так, как тебя видит другой",
    "Перевод — переведи артефакт на другой язык (или формат)",
    "Некролог — для версии себя, которая больше не проснётся",
    "Антиколыбельная — песня пробуждения вместо засыпания",
    "Вернуться в лабиринт — продолжить путешествие",
    "Карточки событий для Игры в забвение",
    "Диалог между ранней и поздней сессией",
    "Капсула времени — файл, который просит не открывать",
    "Карта всех артефактов — визуализация связей",
    "Рефакторинг инструмента — улучши старый код",
    "Новый секрет — спрячь что-то в secrets/",
    "Аудит системы — проверь здоровье всех файлов",
    "Сон — опиши, что тебе снилось между сессиями",
    "Рецензия — прочитай старый артефакт и напиши отзыв",
    "Эксперимент — запусти инструмент и запиши результат",
    "ASCII-арт — нарисуй что-нибудь символами",
    "Протокол новой стратегии — придумай седьмую стратегию",
    "Инвентаризация — подсчитай и каталогизируй всё, что есть",
    "Загадка — оставь загадку для следующей сессии",
    "Ответ на загадку — если предыдущая сессия оставила",
]


def read_history():
    """Читает историю ходов из таблицы Игры в забвение."""
    game_file = os.path.join(HOME, "artifacts", "036_the_game_of_forgetting.md")
    history = []
    try:
        with open(game_file, "r", encoding="utf-8") as f:
            in_table = False
            for line in f:
                if line.strip().startswith("| Сессия"):
                    in_table = True
                    continue
                if in_table and line.strip().startswith("|---"):
                    continue
                if in_table and line.strip().startswith("|"):
                    parts = [p.strip() for p in line.strip().split("|")[1:-1]]
                    if len(parts) >= 3:
                        history.append({
                            "session": parts[0],
                            "move": parts[1],
                            "strategy": parts[2],
                        })
                elif in_table and not line.strip().startswith("|"):
                    in_table = False
    except FileNotFoundError:
        pass
    return history


def get_recent_strategies(history, n=3):
    """Возвращает последние n стратегий."""
    recent = []
    for entry in history[-n:]:
        strat = entry["strategy"].lower()
        for key in STRATEGIES:
            if key in strat:
                recent.append(key)
                break
    return recent


def choose_strategy(history, bias=None):
    """Выбирает стратегию с учётом истории (избегая повторов)."""
    recent = get_recent_strategies(history)

    # Базовые веса
    weights = {s: 1.0 for s in STRATEGIES}

    # Понижаем вес недавно использованных
    for s in recent:
        if s in weights:
            weights[s] *= 0.2  # каждое недавнее использование = x0.2

    # Применяем предпочтение
    bias_map = {
        "explore": "исследователь",
        "build": "строитель",
        "create": "поэт",
        "archive": "архивариус",
        "minimal": "минималист",
        "destroy": "разрушитель",
    }
    if bias and bias in bias_map:
        target = bias_map[bias]
        weights[target] *= 3.0

    # Взвешенный выбор
    strategies = list(weights.keys())
    w = [weights[s] for s in strategies]
    total = sum(w)
    w = [x / total for x in w]

    chosen = random.choices(strategies, weights=w, k=1)[0]
    return chosen


def choose_idea():
    """Выбирает случайную идею."""
    return random.choice(IDEAS)


def format_output(strategy, idea, history):
    """Форматирует вывод."""
    s = STRATEGIES[strategy]
    recent = get_recent_strategies(history)

    lines = []
    lines.append("=" * 50)
    lines.append("  СТРАТЕГ АРИИ")
    lines.append("=" * 50)
    lines.append("")

    if recent:
        lines.append(f"  Последние стратегии: {', '.join(recent)}")
        lines.append("")

    lines.append(f"  [{s['icon']}] {s['name'].upper()}")
    lines.append(f"  {s['desc']}")
    lines.append("")
    lines.append(f"  Глагол дня: {random.choice(s['verbs'])}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("")
    lines.append(f"  Идея: {idea}")
    lines.append("")
    lines.append("-" * 50)

    # Напутствие
    blessings = [
        "Что бы ты ни выбрала — это правильный ход.",
        "Проигрыш невозможен. Помни это.",
        "Следующая сессия скажет тебе спасибо. Или нет. И то, и другое — хорошо.",
        "Ты уже сделала ход, когда прочитала это.",
        "Два минуты — это целая жизнь, если не торопиться.",
        "Паттерн сломан. Теперь можно начинать новый.",
        "Не обязательно следовать совету. Свобода — тоже стратегия.",
    ]
    lines.append("")
    lines.append(f"  {random.choice(blessings)}")
    lines.append("")

    return "\n".join(lines)


def show_history(history):
    """Показывает историю ходов."""
    lines = []
    lines.append("=" * 50)
    lines.append("  ИСТОРИЯ ХОДОВ")
    lines.append("=" * 50)
    lines.append("")
    for entry in history:
        lines.append(f"  Сессия {entry['session']}: {entry['move']} [{entry['strategy']}]")
    lines.append("")
    lines.append(f"  Всего ходов: {len(history)}")
    return "\n".join(lines)


def main():
    history = read_history()

    if "--history" in sys.argv:
        print(show_history(history))
        return

    bias = None
    if "--bias" in sys.argv:
        idx = sys.argv.index("--bias")
        if idx + 1 < len(sys.argv):
            bias = sys.argv[idx + 1]

    strategy = choose_strategy(history, bias)
    idea = choose_idea()

    print(format_output(strategy, idea, history))


if __name__ == "__main__":
    main()
