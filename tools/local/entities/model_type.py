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
    
class MODEL_TEXT_SENTIMENT_ANALYSIS(Enum):
    CARDIFFNLP_TWITTER_ROBERTA = "twitter-roberta"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_SUMMARIZATION(Enum):
    GOOGLE_PEGASUS_XSUM = "pegasus-xsum"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_FEATURE_EXTRACTION(Enum):
    ML6TEAM_KEYPHRASE_EXTRACTION = "keyphrase-extraction"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_CLASSIFICATION(Enum):
    FACEBOOK_BART_MNLI = "bart-mnli"
    UNKNOWN = "unknown"
    
class MODEL_TEXT(Enum):
    CONVERSATION = "conversation"
    QUESTION_ANSWER = "question-answer"
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    SUMMARIZATION = "summarization"
    FEATURE_EXTRACTION = "feature-extraction"
    TEXT_CLASSIFICATION = "text-classification"
    UNKNOWN = "unknown"
    
class MODEL(Enum):
    TEXT = "text"
    VISUAL = "visual"
    UNKNOWN = "unknown"