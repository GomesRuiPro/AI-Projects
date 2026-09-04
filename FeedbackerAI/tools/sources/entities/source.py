from dataclasses import dataclass, field
from inspect import ismethod
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.agents.entities.component import ComponentData
from typing import List

@dataclass
class SourceAnswer(Answer):
    pass

@dataclass
class SourceQuestion(Question):
    pass
    
@dataclass
class SourceData(ComponentData):
    answers: List[SourceAnswer] = field(default_factory=list)
    questions: List[SourceQuestion] = field(default_factory=list)
    