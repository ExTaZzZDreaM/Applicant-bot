# Status Bot

Telegram-бот для проверки статуса заявки на кинопроект по ИИН/БИН через Google Sheets.

## Требования

- Python 3.10+
- Telegram Bot Token (через [@BotFather](https://t.me/BotFather))
- Google Cloud service account с включёнными API:
  - Google Sheets API
  - Google Drive API

## Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/<username>/status_bot.git
cd status_bot

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать (Windows)
venv\Scripts\activate

# 4. Установить зависимости
pip install aiogram python-dotenv gspread google-auth
```

## Настройка

### 1. Файл `.env`

Создать файл `.env` в корне проекта:

```
BOT_TOKEN=<токен от BotFather>
GOOGLE_CREDENTIALS_FILE=credentials.json
SHEET_KEY=<ID таблицы из URL>
WORKSHEET_NAME=<имя листа>
```

`SHEET_KEY` — строка между `/d/` и `/edit` в URL таблицы:
```
https://docs.google.com/spreadsheets/d/ЭТОТ_ID/edit
```

### 2. Файл `credentials.json`

Скачать JSON-ключ сервисного аккаунта из Google Cloud Console и положить в корень проекта.

### 3. Доступ к таблице

Убедиться, что сервисный аккаунт (email из `credentials.json` → `client_email`) добавлен как **Читатель** в Google Таблице.

## Запуск

```bash
venv\Scripts\python -m app.main
```

### Примечание по нескольким таблицам

Если вам нужно проверять заявки сразу в нескольких таблицах (разделённых по категориям),
используйте новую переменную окружения `SHEETS`.
Формат:

```
SHEETS=категория1:ID1[:имя_листа];категория2:ID2[:имя_листа];...
```

Пример:

```
SHEETS=Игровой фильм:1BgBI-Ccz...:Лист1;Анимация:1C2rD4...;Документальный:1eRiYZ...
```

Если `имя_листа` опущено, будет использовано значение из `WORKSHEET_NAME` (как
в старой версии).

Старая переменная `SHEET_KEY` остаётся поддерживаемой для обратной
совместимости, но при наличии `SHEETS` она игнорируется.
```
Бот начнёт опрос Telegram (polling). Для остановки — `Ctrl+C`.

### Последовательность взаимодействия

1. Пользователь вводит `/start` или `СТАТУС` (кнопка «Статус заявки»).
2. Бот предлагает выбрать категорию кинопроекта (игровой, анимационный, документальный и т.п.).
3. После выбора категории появляется запрос на ввод ИИН/БИН.
4. Поиск выполняется только в таблицах, относящихся к выбранной категории.

Это помогает быстрее находить нужные данные и исключить лишние запросы.

## Структура проекта

```
status_bot/
├── .env                  # Переменные окружения (не в git)
├── .gitignore
├── credentials.json      # Ключ сервисного аккаунта (не в git)
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа
│   ├── config.py         # Загрузка переменных из .env
│   ├── handlers.py       # Обработчики сообщений
│   ├── states.py         # FSM-состояния
│   ├── sheets.py         # Работа с Google Sheets
│   └── texts.py          # Тексты сообщений бота
```
