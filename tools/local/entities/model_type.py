from enum import Enum
from typing import List

class MODEL_VISUAL(Enum):
    MOVEMENT = "movement"
    ENVIRONMENT = "environment"
    OBJECT_DETECTION = "object-detection"
    VISUAL_CLASSIFICATION = "visual-classification"
    UNKNOWN = "unknown"
    
class MODEL_VISUAL_ENVIRONMENT(Enum):
    UNKNOWN = "unknown"
    
class MODEL_VIDEO_CLASSIFICATION(Enum):
    UNKNOWN = "unknown"
    
class MODEL_VISUAL_MOVEMENT(Enum):
    UNKNOWN = "unknown"

class MODEL_VISUAL_OBJECT_DETECTION(Enum):
    MICROSOFT_GLIP = "glip"
    FACEBOOK_DETR = "detr"
    OPENAI_CLIP = "clip"
    UNKNOWN = "unknown"

class MODEL_TEXT_CONVERSATION(Enum):
    OPENAI_GPT2 = "gpt2"
    META_LLAMA_31 = "llama"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_QUESTION_ANSWER(Enum):
    DEEPSET_SQUAD2 = "squad2"
    UNKNOWN = "unknown"
    
class MODEL_TEXT(Enum):
    CONVERSATION = "conversation"
    QUESTION_ANSWER = "question-answer"
    UNKNOWN = "unknown"
    
class MODEL(Enum):
    TEXT = "text"
    VISUAL = "visual"
    UNKNOWN = "unknown"