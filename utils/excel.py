import pandas as pd
import asyncio

excel_lock = asyncio.Lock()

async def read_excel_async(path, **kwargs):
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

async def write_excel_async(df, path, **kwargs):
    async with excel_lock:
        df.to_excel(path, index=False, engine='openpyxl', **kwargs)
