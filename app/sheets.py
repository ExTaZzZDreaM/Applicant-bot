from google.oauth2.service_account import Credentials
import gspread

from app.config import (
    GOOGLE_CREDENTIALS_FILE,
    SHEET_KEY,
    WORKSHEET_NAME,
)

def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=scopes
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_KEY).worksheet(WORKSHEET_NAME)

import re


def _extract_digits(value: str) -> str:
    """Извлекает только цифры из строки: 'БИН 030640011488' -> '030640011488'"""
    return re.sub(r"\D", "", str(value))


def find_by_iin(iin: str):
    sheet = get_sheet()
    rows = sheet.get_all_records()

    for row in rows:
        cell_digits = _extract_digits(row.get("БИН или ИИН", ""))
        if cell_digits == iin:
            return row

    return None