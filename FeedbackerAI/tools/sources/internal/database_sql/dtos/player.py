from dataclasses import dataclass
from innovation.FeedbackerAi.tools.local.entities.age_group import AGE_GROUP
from innovation.FeedbackerAi.tools.local.entities.gender import GENDER
from innovation.FeedbackerAi.tools.local.entities.region import REGION
    
@dataclass
class Player:
    name: str
    gender: GENDER
    age_group: AGE_GROUP
    region: REGION