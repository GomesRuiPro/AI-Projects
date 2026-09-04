from dataclasses import dataclass
from enum import Enum
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
    
@dataclass
class Source:
    name: str
    source_type: SOURCE_TYPE
    