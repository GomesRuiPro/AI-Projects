from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer
from innovation.FeedbackerAi.tools.sources.entities.source import SourceQuestion
@dataclass
class Browser:
    question: SourceQuestion
    answer: SourceAnswer
    
@dataclass
class BrowserAnswer(SourceAnswer):
    pass
@dataclass
class BrowserQuestion(SourceQuestion):
    pass
    