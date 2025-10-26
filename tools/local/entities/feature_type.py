from enum import Enum
from typing import List
from innovation.FeedbackerAi.tools.local.entities.feature import GENERIC

class TYPE(Enum):
    GENERAL = ("general", list(GENERIC))
    GAMEPLAY = ("gameplay", [])
    GRAPHICS = ("graphics", [])
    SOUND = ("sound", [])
    UI = ("ui", [])
    TECHNICAL = ("technical", [])
    SOCIAL = ("social", [])
    MONETIZATION = ("monetization", [])
    STORY = ("story", [])
    INNOVATION = ("innovation", [])
    OTHER = ("other", [])
    
    def __init__(self, description, features):
        self.description = description
        self.features: List[GENERIC] = features