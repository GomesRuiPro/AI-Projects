
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
import json
from dataclasses import asdict, is_dataclass

@dataclass(eq=True)
class Trend:
    id: uuid = field(init=False)
    name: str
    feature_type: FEATURE_TYPE = field(init=False, default=FEATURE.UNKNOWN)
    amount: int = field(init=False, default=1)
    review: object = field(init=False, default=None)
    
    def __init__(self, name: str):
        self.name = name
        self.id = uuid.uuid4()
        self.amount = 1
        self.feature_type = FEATURE.UNKNOWN
        self.review = None
        
    def toString(self):
        return [f"{name} = {value}" for name, value in vars(self).items()]
    
    def increment_amount(self):
        self.amount += 1
        return self.amount
        
    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Trend):
            return None
        return self.name == other.name
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "feature_type": self.feature_type.name,
            "amount": self.amount,
            "review_id": str(self.review.id)
        }
    
@dataclass(eq=True)
class Review:
    
    id: uuid = field(init=False)
    text: str
    source_type: SOURCE_TYPE = field(default=SOURCE_TYPE.UNKNOWN)
    player_type: PLAYER_TYPE = field(init=False, default=PLAYER_TYPE.UNKNOWN)
    genre: GENRE = field(default=GENRE.UNKNOWN)
    platform: PLATFORM = field(default=PLATFORM.UNKNOWN)
    focus: FEATURE_TYPE = field(default=FEATURE.UNKNOWN)
    sentiment: REVIEW_SENTIMENT = field(init=False, default=REVIEW_SENTIMENT.UNKNOWN)
    trends: List[Trend] = field(init=False, default_factory=list)
    
    def __init__(self, text: str, genre, platform, source_type, focus):
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
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "text": self.text,
            "genre": self.genre,
            "source_type": self.source_type.name,
            "player_type": self.player_type.name,
            "platform": self.platform.name,
            "focus": self.focus.name,
            "sentiment": self.sentiment.name,
            "trends": ",".join([trend.name for trend in self.trends]),
        }
