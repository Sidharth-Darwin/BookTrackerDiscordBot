import csv
import gspread
from gspread_dataframe import set_with_dataframe
from config import GOOGLE_SHEETS_CRED_PATH, GOOGLE_SHEET_NAME, GOOGLE_SHEET_WORKSHEET, GENRE_FILE
from utils.excel import read_excel_async

async def sync_excel_to_google_sheet():
    """
    Syncs the main Excel sheet to a Google Sheet and updates the local genre CSV file
    from the "Genres" worksheet in the Google Sheet.

    Steps:
    1. Connects to Google Sheets using service account credentials.
    2. Opens the target Google Sheet and worksheet.
    3. Reads the Excel file asynchronously and uploads its data to the worksheet.
    4. Fetches the "Genres" worksheet, validates its format, and writes its contents
       to a local CSV file specified by GENRE_FILE.

    Returns:
        tuple: (success: bool, error_message: Optional[str])
            success: True if main sync succeeded (even if genre sync failed).
            error_message: None if all succeeded, or a warning message if genre sync failed.
    """
    gc = gspread.service_account(filename=GOOGLE_SHEETS_CRED_PATH)
    if not GOOGLE_SHEET_NAME:
        raise ValueError("GOOGLE_SHEET_NAME must not be None")
    sh = gc.open(GOOGLE_SHEET_NAME)

    # Sync main Excel sheet
    worksheet = sh.worksheet(GOOGLE_SHEET_WORKSHEET) if GOOGLE_SHEET_WORKSHEET else sh.sheet1
    df = await read_excel_async()
    worksheet.clear()
    set_with_dataframe(worksheet, df)

    # Sync genres from "Genres" sheet to local CSV
    try:
        genre_ws = sh.worksheet("Genres")
        genre_data = genre_ws.get_all_values()

        if not genre_data or genre_data[0][0].strip().lower() != "genres":
            raise ValueError("First column in 'Genres' sheet must be 'Genres'")

        genres = [row[0].strip().lower() for row in genre_data[1:] if row and row[0].strip()]

        with open(GENRE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Genres"])
            for genre in genres:
                writer.writerow([genre])

        return True, None
    except Exception as e:
        return True, f"⚠️ Google Sheet sync succeeded but genre sync failed: {e}"
