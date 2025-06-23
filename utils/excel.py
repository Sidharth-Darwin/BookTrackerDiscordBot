import pandas as pd
import asyncio
from config import EXCEL_FILE, DEBUG

excel_lock = asyncio.Lock()

async def read_excel_async(path=EXCEL_FILE, **kwargs):
    async with excel_lock:
        try:
            df = pd.read_excel(path, **kwargs)
            df["UserID"] = df["UserID"].astype(str)
            return df
        except FileNotFoundError:
            cols = [
                "Date", "UserID", "UserName", "BookName", "Author",
                "Genres", "LastPage", "TotalPages", "LastUpdated",
                "Status", "Rating"
            ]
            df_new = pd.DataFrame(columns=cols)
            df_new.to_excel(path, index=False, engine='openpyxl')
            return df_new

async def write_excel_async(df, path=EXCEL_FILE, **kwargs):
    async with excel_lock:
        df.to_excel(path, index=False, engine='openpyxl', **kwargs)


async def filter_booknames_with_user_status(user_id: str, status: int) -> list[str]:
    if (not user_id) or (status > 2) or (status < 0):
        return []
    if not isinstance(status, int) or status not in [0, 1, 2]:
        if DEBUG:
            print("⚠️ Invalid status provided. Must be 0 (Shelved), 1 (Reading), or 2 (Completed).")
        return []
    try:
        df = await read_excel_async(EXCEL_FILE)
        df["UserID"] = df["UserID"].astype(str)
        filtered = df[(df["UserID"] == user_id) & (df["Status"] == status)]
        return filtered["BookName"].dropna().unique().tolist()
    except Exception as e:
        if DEBUG:
            print(f"⚠️ Error fetching books for {user_id}: {e}")
        return []
    
async def filter_booknames_with_user(user_id: str) -> list[str]:
    if not user_id:
        return []
    try:
        df = await read_excel_async(EXCEL_FILE)
        df["UserID"] = df["UserID"].astype(str)
        filtered = df[df["UserID"] == user_id]
        return filtered["BookName"].dropna().unique().tolist()
    except Exception as e:
        if DEBUG:
            print(f"⚠️ Error fetching books for {user_id}: {e}")
        return []

