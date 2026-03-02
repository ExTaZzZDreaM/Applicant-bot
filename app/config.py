import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")

# Для обратной совместимости сохраним поддержку одиночной таблицы.
# Эти переменные могут оставаться пустыми при использовании SHEETS.
SHEET_KEY = os.getenv("SHEET_KEY")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")

# новый вариант: допускаем несколько таблиц с категориями
# формат переменной окружения:
#   SHEETS=категория1:ID1[:worksheet1];категория2:ID2[:worksheet2];...
# если имя листа не указано, будет использовано WORKSHEET_NAME (старый режим)

SHEETS_ENV = os.getenv("SHEETS", "")


def _parse_sheets_env(value: str) -> list[dict]:
    """Парсит строку из env и возвращает список словарей
    с ключами 'category', 'key' и 'worksheet'.

    Пример:
        Игровой фильм:1BgBI...:Лист1;Анимация:1C2r...
    """
    entries: list[dict] = []
    for part in filter(None, value.split(";")):
        pieces = part.split(":")
        if len(pieces) < 2:
            continue
        category = pieces[0].strip()
        key = pieces[1].strip()
        worksheet = pieces[2].strip() if len(pieces) >= 3 and pieces[2].strip() else WORKSHEET_NAME
        entries.append({
            "category": category,
            "key": key,
            "worksheet": worksheet,
        })
    return entries


SHEETS_INFO = _parse_sheets_env(SHEETS_ENV)
