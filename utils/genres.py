from typing import Set, List
import pandas as pd
from config import GENRE_FILE, DEBUG

GENRE_LIST: List[str] = []
GENRE_SET: Set[str] = set()

def update_genres():
    """Re-reads the genre CSV file and updates GENRE_LIST and GENRE_SET."""
    global GENRE_LIST, GENRE_SET
    try:
        data = pd.read_csv(GENRE_FILE)["Genres"].str.lower().tolist()
        GENRE_LIST = sorted([genre.title() for genre in data])
        GENRE_SET = set(data)
    except Exception as e:
        GENRE_LIST = []
        GENRE_SET = set()
        if DEBUG:
            print(f"⚠️ Failed to update genres from file: {e}")

update_genres()
