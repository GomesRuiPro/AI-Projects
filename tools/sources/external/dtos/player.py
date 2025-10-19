from dataclasses import dataclass
from innovation.FeedbackerAi.tools.sources.external.entities.age_group import AGE_GROUP
from innovation.FeedbackerAi.tools.sources.external.entities.gender import GENDER
from innovation.FeedbackerAi.tools.sources.external.entities.region import REGION
    
@dataclass
class Player:
    name: str
    gender: GENDER
    age_group: AGE_GROUP
    region: REGION