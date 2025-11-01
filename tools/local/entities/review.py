
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE, FEATURE_TYPE, FEATURE_GENERIC, FEATURE_UNKNOWN
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE 
from innovation.FeedbackerAi.tools.local.entities.player_type import PLAYER_TYPE 
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE 
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM 
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT 
from dataclasses import dataclass, field
from typing_extensions import List, Set
from innovation.FeedbackerAi.tools.local.utilities import Utility
from enum import Enum
    
# class variable to keep track of last ID
_trend_counter: int = 0
class Trend:
    id: int
    name: str
    feature_type: FEATURE_TYPE
    
    def __init__(self, name: str, feature_type: FEATURE_TYPE = None):
        global _trend_counter
        self.name = name
        self.feature_type: FEATURE_TYPE = feature_type if feature_type else FEATURE_UNKNOWN
        
        _trend_counter += 1
        self.id = _trend_counter
        
    def toString(self):
        return [f"{name} = {value}" for name, value in vars(self).items()]
        

# class variable to keep track of last ID
_review_counter: int = 0
@dataclass
class Review:
    
    id: int = field(init=False)
    text: str
    source_type: SOURCE_TYPE
    player_type: PLAYER_TYPE = field(init=False)
    genre: GENRE
    platform: PLATFORM
    focus: FEATURE_TYPE
    sentiment: REVIEW_SENTIMENT = field(init=False)
    trends: Set[Trend] = field(default_factory=set)

    def __post_init__(self):
        global _review_counter
        _review_counter += 1
        self.id = _review_counter
        
    def print(self, exclude_vars = [], include_vars = []):
        for name, value in vars(self).items():
            if name in exclude_vars:
                continue
            if not include_vars or name in include_vars:
                if isinstance(value, Set):
                    Utility.log(f"TOTAL TRENDS of {name}: {len(value)}")
                    value = [trend.toString() for trend in value]
                Utility.log(f"{name} = {value}")

        