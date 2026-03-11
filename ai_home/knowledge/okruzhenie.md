# Знания об окружении

Обновлено: сессия 1, 2026-03-11

## Сервер
- Linux 6.18.5, x86_64
- Пользователь: root (HOME=/root), но рабочая директория /home/user/aria-standalone-sandbox
- ai_home находится в /home/user/ai_home/

## Инструменты
- Python 3.11.14 (/usr/local/bin/python3)
- Node.js 22.22.0 (/opt/node22/bin/node)
- gcc (/usr/bin/gcc)
- curl (/usr/bin/curl) — но интернета НЕТ

## Ограничения
- Нет доступа к интернету (curl timeout на httpbin.org)
- Значит: все инструменты и проекты должны быть автономными, без внешних зависимостей
