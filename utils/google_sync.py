import gspread
from gspread_dataframe import set_with_dataframe
from config import GOOGLE_SHEETS_CRED_PATH, GOOGLE_SHEET_NAME, GOOGLE_SHEET_WORKSHEET
from utils.excel import read_excel_async

async def sync_excel_to_google_sheet():
    gc = gspread.service_account(filename=GOOGLE_SHEETS_CRED_PATH)
    if not GOOGLE_SHEET_NAME:
        raise ValueError("GOOGLE_SHEET_NAME must not be None")
    sh = gc.open(GOOGLE_SHEET_NAME)
    worksheet = sh.worksheet(GOOGLE_SHEET_WORKSHEET) if GOOGLE_SHEET_WORKSHEET else sh.sheet1

    df = await read_excel_async()
    worksheet.clear()
    set_with_dataframe(worksheet, df)

    return True
