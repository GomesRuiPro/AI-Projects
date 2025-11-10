from dataclasses import dataclass, field
from inspect import ismethod
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.agents.entities.question import Question

@dataclass
class Source:
    question: Question
    answer: Answer
    
@dataclass
class SourceAnswer:
    text: str
    metadata: dict = field(default_factory=dict)
    
@dataclass
class SourceQuestion:
    text: str
    method_fn: ismethod
    max_results: int
    metadata: dict = field(default_factory=dict)