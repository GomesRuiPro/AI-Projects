from dataclasses import dataclass
from typing import List
from innovation.FeedbackerAi.tools.sources.external.entities.genre import GENRE, SUBGENRE
    
@dataclass
class GameGenre:
    name: GENRE
    sub_genre: List[SUBGENRE]