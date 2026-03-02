from google.oauth2.service_account import Credentials
import gspread

from app.config import (
    GOOGLE_CREDENTIALS_FILE,
    # оставлены для обратной совместимости
    SHEET_KEY,
    WORKSHEET_NAME,
    SHEETS_INFO,
)

def _create_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=scopes
    )
    return gspread.authorize(creds)


def get_sheets(category: str | None = None):
    """Возвращает итератор (sheet, category) для каждой конфигурации.

    Если передан параметр `category`, фильтрует только по нему.
    Поддерживается как новый режим (SHEETS_INFO), так и старый одинарный
    SHEET_KEY/WORKSHEET_NAME для совместимости.
    """
    client = _create_client()

    if SHEETS_INFO:
        for info in SHEETS_INFO:
            cat = info.get("category")
            if category and category != cat:
                continue
            try:
                sheet = client.open_by_key(info["key"]).worksheet(info.get("worksheet"))
            except Exception:
                # если что-то упало, пропускаем, но не даём краху
                continue
            yield sheet, cat
    else:
        # старый режим
        if category is None:
            yield client.open_by_key(SHEET_KEY).worksheet(WORKSHEET_NAME), None
        # иначе ничего не возвращаем

import re
from typing import List, Optional


def get_categories() -> List[str]:
    """Возвращает упорядоченный список уникальных категорий из конфигурации.
    Пустые категории отброшены; если в списке нет ни одной, возвращается [''].
    """
    cats = []
    for _, cat in get_sheets():
        if cat and cat not in cats:
            cats.append(cat)
    return cats if cats else [""]



def _extract_digits(value: str) -> str:
    """Извлекает только цифры из строки: 'БИН 030640011488' -> '030640011488'"""
    return re.sub(r"\D", "", str(value))


def find_by_iin(iin: str, category: str | None = None):
    # ищем во всех конфигурациях (возможны несколько таблиц)
    for sheet, cat in get_sheets(category):
        rows = sheet.get_all_records()
        for row in rows:
            cell_digits = _extract_digits(row.get("БИН или ИИН", ""))
            if cell_digits == iin:
                if cat:
                    row["_category"] = cat
                return row
    return None