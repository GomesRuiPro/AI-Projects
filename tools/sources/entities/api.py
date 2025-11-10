from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer
from innovation.FeedbackerAi.tools.sources.entities.source import SourceQuestion
@dataclass
class Api:
    question: SourceQuestion
    answer: SourceAnswer
    
@dataclass
class ApiAnswer(SourceAnswer):
    pass
@dataclass
class ApiQuestion(SourceQuestion):
    pass