from typing import Sequence
import pandas as pd
from config import GENRE_FILE

GENRE_LIST: Sequence[str] = pd.read_csv(GENRE_FILE)["Genres"].str.lower().tolist()
