from dataclasses import dataclass, field
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.agents.entities.component import ComponentData
from inspect import ismethod
from typing import List


@dataclass
class ModelQuestion(Question):
    pass
    
@dataclass
class ModelAnswer(Answer):
    pass
    
@dataclass
class ModelData(ComponentData):
    answers: List[ModelAnswer] = field(default_factory=list)
    questions: List[ModelQuestion] = field(default_factory=list)