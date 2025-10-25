from enum import Enum
from typing import List

class FEATURE(Enum):
    pass

class GENERIC(FEATURE):
    MULTIPLAYER_SUPPORT = "multiplayer-support"
    SINGLE_PLAYER_MODE = "single-player-mode"
    STORYLINE = "storyline-narrative"
    OPEN_WORLD = "open-world-sandbox-environment"
    ACHIEVEMENTS = "achievements-trophies"
    CUSTOMIZATION = "customizable-characters-avatars"
    PROGRESSION_SYSTEM = "progression-system-leveling-up"
    IN_GAME_ECONOMY = "in-game-economy-currency"
    MICROTRANSACTIONS = "microtransactions-in-app-purchases"
    VOICE_CHAT = "voice-and-text-chat"
    LEADERBOARDS = "leaderboards-rankings"
    CHALLENGES = "daily-weekly-challenges"
    REPLAYABILITY = "replayability-random-generation"
    CROSS_PLATFORM = "cross-platform-play"
    MOD_SUPPORT = "mod-support-custom-content"
    GRAPHICS_CUSTOMIZATION = "graphics-settings-customization"
    CLOUD_SAVING = "cloud-saving"
    TUTORIALS = "tutorials-onboarding"
    SOUNDTRACK = "soundtrack-music"
