from dataclasses import dataclass, field
from innovation.FeedbackerAi.tools.models.entities.model import ModelData, ModelAnswer, ModelQuestion
from typing import List

    
@dataclass
class TextAnswer(ModelAnswer):
    pass

@dataclass
class TextQuestion(ModelQuestion):
    pass

@dataclass
class TextData(ModelData):
    answers: List[TextAnswer] = field(default_factory=list)
    questions: List[TextQuestion] = field(default_factory=list)