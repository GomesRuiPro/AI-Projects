from enum import Enum
from typing import List

class MODEL_TYPE(Enum):
    def __init__(self, description, submodels: Enum = None):
        super().__init__()
        self.description = description
        self.submodels = submodels
        
    @classmethod
    def __getitem__(cls, item):
        # Override to make lookups case-insensitive
        item = item.upper()
        return super().__getitem__(item)
    
class MODEL_VISUAL_ENVIRONMENT(MODEL_TYPE):
    UNKNOWN = "unknown"
    
class MODEL_VISUAL_CLASSIFICATION(MODEL_TYPE):
    UNKNOWN = "unknown"
    
class MODEL_VISUAL_MOVEMENT(MODEL_TYPE):
    UNKNOWN = "unknown"

class MODEL_VISUAL_OBJECT_DETECTION(MODEL_TYPE):
    MICROSOFT_GLIP = "glip"
    FACEBOOK_DETR = "detr"
    OPENAI_CLIP = "clip"
    UNKNOWN = "unknown"
    
class MODEL_VISUAL(MODEL_TYPE):
    MOVEMENT = "movement", MODEL_VISUAL_MOVEMENT
    ENVIRONMENT = "environment", MODEL_VISUAL_ENVIRONMENT
    OBJECT_DETECTION = "object-detection", MODEL_VISUAL_OBJECT_DETECTION
    VISUAL_CLASSIFICATION = "visual-classification", MODEL_VISUAL_CLASSIFICATION
    UNKNOWN = "unknown"

class MODEL_TEXT_CONVERSATION(MODEL_TYPE):
    OPENAI_GPT2 = "gpt2"
    META_LLAMA_31 = "llama"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_QUESTION_ANSWER(MODEL_TYPE):
    DEEPSET_SQUAD2 = "squad2"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_TRANSLATION(MODEL_TYPE):
    GOOGLE_MT5 = "mt5"
    FACEBOOK_MULTILANG_NLLB = "nllb"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_SENTIMENT_ANALYSIS(Enum):
    CARDIFFNLP_TWITTER_ROBERTA = "twitter-roberta"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_SUMMARIZATION(Enum):
    GOOGLE_PEGASUS_XSUM = "pegasus-xsum"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_FEATURE_EXTRACTION(Enum):
    ML6TEAM_KEYPHRASE_EXTRACTION = "keyphrase-extraction"
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    UNKNOWN = "unknown"
    
class MODEL_TEXT_CLASSIFICATION(Enum):
    FACEBOOK_BART_MNLI = "bart"
    MICROSOFT_DEBERTA_MNLI = "deberta"
    UNKNOWN = "unknown"
    
class MODEL_TEXT(MODEL_TYPE):
    CONVERSATION = "conversation", MODEL_TEXT_CONVERSATION
    QUESTION_ANSWER = "question-answer", MODEL_TEXT_QUESTION_ANSWER
    SENTIMENT_ANALYSIS = "sentiment-analysis", MODEL_TEXT_SENTIMENT_ANALYSIS
    TRANSLATION = "translation", MODEL_TEXT_TRANSLATION
    SUMMARIZATION = "summarization", MODEL_TEXT_SUMMARIZATION
    FEATURE_EXTRACTION = "feature-extraction", MODEL_TEXT_FEATURE_EXTRACTION
    TEXT_CLASSIFICATION = "text-classification", MODEL_TEXT_CLASSIFICATION
    UNKNOWN = "unknown"
    
class MODEL(MODEL_TYPE):
    TEXT = "text", MODEL_TEXT
    VISUAL = "visual", MODEL_VISUAL
    UNKNOWN = "unknown"