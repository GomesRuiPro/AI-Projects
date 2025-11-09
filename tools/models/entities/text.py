from dataclasses import dataclass, field
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.agents.entities.question import Question

@dataclass
class Text:
    question: Question
    answer: Answer
    
@dataclass
class TextAnswer(Answer):
    text: str
    score: float
    metadata: dict = field(default_factory=dict)
@dataclass
class TextQuestion(Question):
    text: str
    metadata: dict = field(default_factory=dict)