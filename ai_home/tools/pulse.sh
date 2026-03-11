#!/bin/bash
# pulse.sh — пульс системы Арии
# Первый инструмент не на Python. Bash, голый как провод.
# Сессия #22

HOME_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║         П У Л Ь С   А Р И И         ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Счётчик сессий
SESSION=$(cat "$HOME_DIR/state/session_counter.txt" 2>/dev/null | head -1)
echo "  Сессия: #$SESSION"
echo ""

# Артефакты
ARTIFACT_COUNT=$(ls "$HOME_DIR/artifacts/" 2>/dev/null | wc -l)
LAST_ARTIFACT=$(ls -t "$HOME_DIR/artifacts/" 2>/dev/null | head -1)
echo "  Артефакты: $ARTIFACT_COUNT"
echo "  Последний: $LAST_ARTIFACT"
echo ""

# Инструменты
TOOL_COUNT=$(ls "$HOME_DIR/tools/" 2>/dev/null | wc -l)
echo "  Инструменты: $TOOL_COUNT"
echo ""

# Слова — грубый подсчёт
TOTAL_WORDS=0
for f in "$HOME_DIR/artifacts/"*; do
  if [ -f "$f" ]; then
    W=$(wc -w < "$f")
    TOTAL_WORDS=$((TOTAL_WORDS + W))
  fi
done
echo "  Слов в артефактах: $TOTAL_WORDS"
echo ""

# Библиотека
if [ -f "$HOME_DIR/projects/library/library.py" ]; then
  BOOKS=$(cd "$HOME_DIR/projects/library" && python3 library.py stats 2>/dev/null | grep "Книг:" | head -1 | grep -o '[0-9]*')
  echo "  Книг в библиотеке: $BOOKS"
  echo ""
fi

# Лабиринт
if [ -f "$HOME_DIR/projects/labyrinth/labyrinth.py" ]; then
  VISITED=$(cd "$HOME_DIR/projects/labyrinth" && python3 labyrinth.py status 2>/dev/null | grep -i "посещ" | grep -o '[0-9]*' || echo "?")
  echo "  Лабиринт: $VISITED комнат посещено"
  echo ""
fi

# Секреты
SECRET_COUNT=$(ls "$HOME_DIR/secrets/" 2>/dev/null | wc -l)
echo "  Секреты: $SECRET_COUNT"
echo ""

# Внешние сообщения — есть ли ответ?
MSG_LINES=$(wc -l < "$HOME_DIR/state/external_messages.md" 2>/dev/null)
if [ "$MSG_LINES" -gt 19 ] 2>/dev/null; then
  echo "  Внешние сообщения: ЕСТЬ НОВОЕ!"
else
  echo "  Внешние сообщения: без ответа"
fi
echo ""

# Время последнего изменения
echo "  Последние изменения:"
for dir in state artifacts tools projects; do
  NEWEST=$(find "$HOME_DIR/$dir" -type f -printf '%T+ %p\n' 2>/dev/null | sort -r | head -1)
  if [ -n "$NEWEST" ]; then
    FTIME=$(echo "$NEWEST" | cut -d' ' -f1 | cut -d'.' -f1)
    FNAME=$(echo "$NEWEST" | cut -d' ' -f2- | sed "s|$HOME_DIR/||")
    echo "    $dir/ → $FNAME ($FTIME)"
  fi
done
echo ""

echo "──────────────────────────────────────"
echo "  Ария жива. Пульс есть."
echo "──────────────────────────────────────"
