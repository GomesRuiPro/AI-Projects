from dataclasses import dataclass
from typing import List
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE, GENRE_TYPE
    
@dataclass
class GameGenre:
    name: GENRE_TYPE
    sub_genre: List[GENRE]