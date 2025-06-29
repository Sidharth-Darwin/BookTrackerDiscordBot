import pandas as pd
import asyncio
from config import EXCEL_FILE, DEBUG

excel_lock = asyncio.Lock()

async def read_excel_async(path=EXCEL_FILE, **kwargs):
    """
    Asynchronously reads an Excel file into a pandas DataFrame.

    If the specified Excel file does not exist, creates a new DataFrame with predefined columns,
    writes it to the file, and returns the new DataFrame.

    Args:
        path (str, optional): Path to the Excel file. Defaults to EXCEL_FILE.
        **kwargs: Additional keyword arguments passed to `pd.read_excel`.

    Returns:
        pandas.DataFrame: The DataFrame read from the Excel file, or a new DataFrame if the file does not exist.

    Raises:
        Any exception raised by `pd.read_excel` other than FileNotFoundError will propagate.

    Note:
        The function ensures that the "UserID" column is of string type.
        Access to the Excel file is synchronized using `excel_lock`.
    """
    async with excel_lock:
        try:
            df = pd.read_excel(path, **kwargs)
            df["UserID"] = df["UserID"].astype(str)
            return df
        except FileNotFoundError:
            cols = [
                "Date", "UserID", "UserName", "BookName", "Author",
                "Genres", "LastPage", "TotalPages", "LastUpdated",
                "Status"
            ]
            df_new = pd.DataFrame(columns=cols)
            df_new.to_excel(path, index=False, engine='openpyxl')
            return df_new

async def write_excel_async(df, path=EXCEL_FILE, **kwargs):
    """
    Asynchronously writes a pandas DataFrame to an Excel file.

    This function acquires an asynchronous lock to ensure thread-safe writing
    to the specified Excel file. It uses the 'openpyxl' engine by default.

    Args:
        df (pandas.DataFrame): The DataFrame to write to the Excel file.
        path (str, optional): The file path where the Excel file will be saved.
            Defaults to EXCEL_FILE.
        **kwargs: Additional keyword arguments to pass to pandas.DataFrame.to_excel().

    Raises:
        Any exception raised by pandas.DataFrame.to_excel() will be propagated.

    Note:
        This function must be called within an async context.
    """
    async with excel_lock:
        df.to_excel(path, index=False, engine='openpyxl', **kwargs)


async def filter_booknames_with_user_status(user_id: str, status: int) -> list[str]:
    """
    Filters and returns a list of unique book names for a given user and reading status.

    Args:
        user_id (str): The ID of the user whose books are to be filtered.
        status (int): The reading status to filter by.
            - 0: Shelved
            - 1: Reading
            - 2: Completed

    Returns:
        list[str]: A list of unique book names matching the user and status criteria.
                   Returns an empty list if the user_id is invalid, the status is out of range,
                   or if an error occurs during processing.

    Raises:
        None. All exceptions are caught and logged if DEBUG is enabled.

    Notes:
        - The function expects the existence of a global EXCEL_FILE variable and a read_excel_async function.
        - The DataFrame is expected to have "UserID", "Status", and "BookName" columns.
        - If DEBUG is enabled, error and warning messages are printed to the console.
    """
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
    """
    Filters and returns a list of unique book names associated with a given user ID from an Excel file.

    Args:
        user_id (str): The user ID to filter book names by.

    Returns:
        list[str]: A list of unique book names associated with the specified user ID. 
                   Returns an empty list if the user ID is not provided or if an error occurs.

    Raises:
        Exception: Any exception encountered during the reading or processing of the Excel file is caught and handled internally.
    """
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

