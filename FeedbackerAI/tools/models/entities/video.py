from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set
from innovation.FeedbackerAi.tools.models.entities.model import ModelData, ModelQuestion, ModelAnswer

from torch import Tensor

@dataclass()
class ClassifiedLabel:
    label: str
    feature_type: str
    score: float = field(default=0.0)
    debug_box: Tensor = field(default=None)
    
@dataclass
class VideoAnswer(ModelAnswer):
    classified_labels: List[ClassifiedLabel] = field(default_factory=list)

@dataclass
class VideoQuestion(ModelQuestion):
    video_frames: List[Tensor] = field(default_factory=list)

@dataclass
class VideoData(ModelData):
    answers: List[VideoAnswer] = field(default_factory=list)
    questions: List[VideoQuestion] = field(default_factory=list)