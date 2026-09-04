from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer
from innovation.FeedbackerAi.tools.sources.entities.source import SourceQuestion
from innovation.FeedbackerAi.agents.entities.component import ComponentData
    
@dataclass
class ApiAnswer(SourceAnswer):
    pass
@dataclass
class ApiQuestion(SourceQuestion):
    pass
@dataclass
class ApiData(ComponentData):
    answers: List[ApiAnswer] = field(default_factory=list)
    questions: List[ApiQuestion] = field(default_factory=list)