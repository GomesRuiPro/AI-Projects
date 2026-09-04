from enum import Enum
from dataclasses import dataclass
from game_genre import GameGenre
from source import Source
from player import Player

@dataclass
class Review:
    game_genre: GameGenre
    source: Source
    player: Player
    score: int
    comments: str