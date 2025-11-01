from enum import Enum
from typing import List

class GENRE_TYPE(Enum):
    def __init__(self, description, subgenres: Enum = None):
        super().__init__()
        self.description = description
        self.subgenres = subgenres
    
    @classmethod
    def __getitem__(cls, item):
        # Override to make lookups case-insensitive
        item = item.upper()
        return super().__getitem__(item)

class SUBGENRE_ACTION(GENRE_TYPE):
    class SUBGENRE_FIGHTING(GENRE_TYPE):
        BEAT_EM_UP = "beat 'em up"
        UNKNOWN = "fighting"
    
    class SUBGENRE_SHOOTER(GENRE_TYPE):
        FIRST_PERSON_SHOOTER = "first-person-shooter"
        THIRD_PERSON_SHOOTER = "third-person-shooter"
        TACTICAL_SHOOTER = "tactical-fps"
        UNKNOWN = "shooter"
    
    PLATFORMER = "platformer"
    FIGHTING = "fighting", SUBGENRE_FIGHTING
    SHOOTER = "shooter", SUBGENRE_SHOOTER
    ACTION_ADVENTURE = "action-adventure"
    STEALTH = "stealth"
    SURVIVAL = "survival"
    ROGUELITE = "roguelite"
    ROGUELIKE = "roguelike"
    UNKNOWN = "action"
    

class SUBGENRE_ADVENTURE(GENRE_TYPE):
    VISUAL_NOVEL = "visual-novel"
    EXPLORATION = "exploration"
    NARRATIVE_DRIVEN = "narrative-driven"
    UNKNOWN = "adventure"

class SUBGENRE_RPG(GENRE_TYPE):
    WESTERN_RPG = "western-rpg"
    JRPG = "jrpg"
    ACTION_RPG = "action-rpg"
    TACTICAL_RPG = "tactical-rpg"
    UNKNOWN = "rpg"

class SUBGENRE_PUZZLE(GENRE_TYPE):
    LOGIC = "logic"
    MATCH_3 = "match-3"
    PHYSICS_BASED = "physics-based"
    UNKNOWN = "puzzle"

class SUBGENRE_STRATEGY(GENRE_TYPE):
    TURN_BASED_STRATEGY = "turn-based-strategy"
    REAL_TIME_STRATEGY = "real-time-strategy"
    TOWER_DEFENSE = "tower-defense"
    X_GAMES = "4x-games"
    UNKNOWN = "strategy"

class SUBGENRE_SIMULATION(GENRE_TYPE):
    LIFE_SIMULATION = "life-simulation"
    FLIGHT_SIMULATION = "flight-simulation"
    FARMING_SIMULATION = "farming-simulation"
    SANDBOX = "sandbox"
    UNKNOWN = "simulation"

class SUBGENRE_SPORTS(GENRE_TYPE):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    EXTREME_SPORTS = "extreme-sports"
    UNKNOWN = "sports"
    
class GENRE(GENRE_TYPE):
    ACTION = "action", SUBGENRE_ACTION
    ADVENTURE = "adventure", SUBGENRE_ADVENTURE
    ROLE_PLAYING = "roleplaying", SUBGENRE_RPG
    PLATFORMER = "platformer"
    PUZZLE = "puzzle", SUBGENRE_PUZZLE
    MUSIC_RHYTHM = "music-rythim"
    STRATEGY = "strategy", SUBGENRE_STRATEGY
    SIMULATION = "simulation", SUBGENRE_SIMULATION
    SPORTS = "sports", SUBGENRE_SPORTS
    RACING = "racing"
    MOBA = "multiplayer-online-battle-arena"
    MMO = "massively-multiplayer-online"
    BATTLE_ROYALE = "battle-royale"
    CARD_GAMES = "cards"
    CASINO = "casino"
    EDUCATIONAL = "educational"
    INDIE = "indie"