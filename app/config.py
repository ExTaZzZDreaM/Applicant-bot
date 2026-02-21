import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
SHEET_KEY = os.getenv("SHEET_KEY")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")