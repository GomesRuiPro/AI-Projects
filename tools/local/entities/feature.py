from enum import Enum
from typing import List

class FEATURE_TYPE(Enum):
    def __init__(self, description, subfeatures: Enum = None):
        super().__init__()
        self.description = description
        self.subfeatures = subfeatures
        
    @classmethod
    def __getitem__(cls, item):
        item_upper = item.upper()
        for member in cls:
            if member.name.upper() == item_upper:
                return member
        raise KeyError(f"{item} not found in {cls.__name__}")

class FEATURE_GENERIC(FEATURE_TYPE):
    GAMEPLAY = "gameplay"
    GRAPHICS = "graphics"
    SOUND = "sound"
    UI = "ui"
    TECHNICAL = "technical"
    SOCIAL = "social"
    CONTENT = "content"
    STORY = "story"
    
class FEATURE_GAMEPLAY(FEATURE_TYPE):
    pass
class FEATURE_GRAPHICS(FEATURE_TYPE):
    pass
class FEATURE_SOUND(FEATURE_TYPE):
    pass
class FEATURE_UI(FEATURE_TYPE):
    pass
class FEATURE_SOCIAL(FEATURE_TYPE):
    pass
class FEATURE_CONTENT(FEATURE_TYPE):
    pass
class FEATURE_STORY(FEATURE_TYPE):
    pass
class FEATURE_MONETIZATION(FEATURE_TYPE):
    pass
class FEATURE_UNKNOWN(FEATURE_TYPE):
    pass
class FEATURE_TECHNICAL(FEATURE_TYPE):
    MONETIZATION = "monetization", FEATURE_MONETIZATION
        
class FEATURE(FEATURE_TYPE):
    GENERAL = "general", FEATURE_GENERIC
    GAMEPLAY = "gameplay", FEATURE_GAMEPLAY
    GRAPHICS = "graphics", FEATURE_GRAPHICS
    SOUND = "sound", FEATURE_SOUND
    UI = "ui", FEATURE_UI
    TECHNICAL = "technical", FEATURE_TECHNICAL
    SOCIAL = "social", FEATURE_SOCIAL
    STORY = "story", FEATURE_STORY
    CONTENT = "content",
    UNKNOWN = "unknown", FEATURE_UNKNOWN

    def get_subfeatures_descriptions(self) -> List[str]:
        if self.subfeatures:
            return [subfeature.description for subfeature in self.subfeatures]
        return []
    # INNOVATION = ("innovation", [])
    # OTHER = ("other", [])
    
    # def __init__(self, description, features=[]):
    #     self.description = description
    #     self.features: List[FEATURE] = features
    
    # def filter(self, features_found: List[str]):
    #     filtered_features = []
    #     if self.subfeatures:
    #         for feature_keywords in self.subfeatures:
    #             filtered_features.extend(Utility.intersect_lists_by_strings(features_found, feature_keywords.keywords))
            
    #     return filtered_features