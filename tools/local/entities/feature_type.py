from enum import Enum
from typing import List
from innovation.FeedbackerAi.tools.local.entities.feature import GENERIC, FEATURE
from innovation.FeedbackerAi.tools.local.utilities import Utility

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
    # INNOVATION = ("innovation", [])
    # OTHER = ("other", [])
    
    def __init__(self, description, features=[]):
        self.description = description
        self.features: List[FEATURE] = features
        
    def get_features_names(self):
        features_names = []
        for feature in self.features:
            features_names.append(feature.description)
        return features_names
    
    def filter(self, features_found: List[str]):
        filtered_features = []
        for feature_keywords in self.features:
            filtered_features.extend(Utility.intersect_lists_by_strings(features_found, feature_keywords.keywords))
            
        return filtered_features