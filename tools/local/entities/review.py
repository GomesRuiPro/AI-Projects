
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE, FEATURE_TYPE, FEATURE_GENERIC, FEATURE_UNKNOWN
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE 
from innovation.FeedbackerAi.tools.local.entities.player_type import PLAYER_TYPE 
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE 
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM 
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT 
from dataclasses import dataclass, field
from typing_extensions import List, Set, Optional
from innovation.FeedbackerAi.tools.local.utilities import Utility
from enum import Enum   
import uuid     

@dataclass(eq=True)
class Trend:
    id: uuid
    name: str
    feature_type: FEATURE_TYPE
    amount: int = field(init=False)
    review: Optional['Review']
    
    def __init__(self, name: str, feature_type: FEATURE_TYPE = None, review=None):
        self.name = name
        self.feature_type: FEATURE_TYPE = feature_type if feature_type else FEATURE_UNKNOWN
        self.amount = 1
        self.review = review
        self.id = uuid.uuid4()
        
    def toString(self):
        return [f"{name} = {value}" for name, value in vars(self).items()]
    
    def increment_amount(self):
        self.amount += 1
        
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Trend):
            return None
        return self.name == other.name
    
@dataclass(eq=True)
class Review:
    
    id: uuid
    text: str
    source_type: SOURCE_TYPE
    player_type: PLAYER_TYPE = field(init=False)
    genre: GENRE
    platform: PLATFORM
    focus: FEATURE_TYPE
    sentiment: REVIEW_SENTIMENT = field(init=False)
    trends: List[Trend] = field(init=False)
    
    def __init__(self, text: str, genre: GENRE = None, platform: PLATFORM = None, source_type: SOURCE_TYPE = None, focus: FEATURE_TYPE = None):
        self.text = text
        self.genre = genre
        self.focus = focus
        self.source_type = source_type
        self.platform = platform
        self.trends = list()
        self.id = uuid.uuid4()
        
    def print(self, exclude_vars = [], include_vars = []):
        for name, value in vars(self).items():
            if name in exclude_vars:
                continue
            if not include_vars or name in include_vars:
                if isinstance(value, List):
                    Utility.log(f"TOTAL TRENDS of {name}: {len(value)}")
                    value = [trend.toString() for trend in value]
                Utility.log(f"{name} = {value}")
                
    def __hash__(self):
        return hash(self.text)

    def __eq__(self, other):
        if not isinstance(other, Review):
            return None
        return self.text == other.text
    
        