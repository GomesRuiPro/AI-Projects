from enum import Enum
from typing import List

class SUBGENRE(Enum):
    pass

class SUBGENRE_ACTION(SUBGENRE):
    class SUBGENRE_FIGHTING(SUBGENRE):
        BEAT_EM_UP = "beat 'em up"
        UNKNOWN = "fighting"
    
    class SUBGENRE_SHOOTER(SUBGENRE):
        FIRST_PERSON_SHOOTER = "first-person-shooter"
        THIRD_PERSON_SHOOTER = "third-person-shooter"
        TACTICAL_SHOOTER = "tactical-fps"
        UNKNOWN = "shooter"
    
    PLATFORMER = "platformer"
    FIGHTING = List[SUBGENRE_SHOOTER]
    SHOOTER = List[SUBGENRE_SHOOTER]
    ACTION_ADVENTURE = "action-adventure"
    STEALTH = "stealth"
    SURVIVAL = "survival"
    ROGUELITE = "roguelite"
    ROGUELIKE = "roguelike"
    UNKNOWN = "action"
    

class SUBGENRE_ADVENTURE(SUBGENRE):
    VISUAL_NOVEL = "visual-novel"
    EXPLORATION = "exploration"
    NARRATIVE_DRIVEN = "narrative-driven"
    UNKNOWN = "adventure"

class SUBGENRE_RPG(SUBGENRE):
    WESTERN_RPG = "western-rpg"
    JRPG = "jrpg"
    ACTION_RPG = "action-rpg"
    TACTICAL_RPG = "tactical-rpg"
    UNKNOWN = "rpg"

class SUBGENRE_PUZZLE(SUBGENRE):
    LOGIC = "logic"
    MATCH_3 = "match-3"
    PHYSICS_BASED = "physics-based"
    UNKNOWN = "puzzle"

class SUBGENRE_STRATEGY(SUBGENRE):
    TURN_BASED_STRATEGY = "turn-based-strategy"
    REAL_TIME_STRATEGY = "real-time-strategy"
    TOWER_DEFENSE = "tower-defense"
    X_GAMES = "4x-games"
    UNKNOWN = "strategy"

class SUBGENRE_SIMULATION(SUBGENRE):
    LIFE_SIMULATION = "life-simulation"
    FLIGHT_SIMULATION = "flight-simulation"
    FARMING_SIMULATION = "farming-simulation"
    SANDBOX = "sandbox"
    UNKNOWN = "simulation"

class SUBGENRE_SPORTS(SUBGENRE):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    EXTREME_SPORTS = "extreme-sports"
    UNKNOWN = "sports"


class GENRE(Enum):
    ACTION: List[SUBGENRE_ACTION]
    ADVENTURE = List[SUBGENRE_ADVENTURE]
    ROLE_PLAYING = List[SUBGENRE_RPG]
    PLATFORMER = "platformer"
    PUZZLE = List[SUBGENRE_PUZZLE]
    MUSIC_RHYTHM = "music-rythim"
    STRATEGY = List[SUBGENRE_STRATEGY]
    SIMULATION = List[SUBGENRE_SIMULATION]
    SPORTS = List[SUBGENRE_SPORTS]
    RACING = "racing"
    MOBA = "multiplayer-online-battle-arena"
    MMO = "massively-multiplayer-online"
    BATTLE_ROYALE = "battle-royale"
    CARD_GAMES = "cards"
    CASINO = "casino"
    EDUCATIONAL = "educational"
    INDIE = "indie"
    
