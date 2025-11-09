from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.agents.entities.answer import Answer
from innovation.FeedbackerAi.agents.entities.question import Question

from torch import Tensor

@dataclass
class Video:
    question: Question
    answer: Answer
    
@dataclass
class ClassifiedLabel:
    label: str
    score: float
    debug_boxes: Tensor = None
    
@dataclass
class VideoAnswer(Answer):
    classified_labels: List[ClassifiedLabel] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
@dataclass
class VideoQuestion(Question):
    video_frames: List[Tensor] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    