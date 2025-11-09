from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.models.object.openai.clip import Clip
from innovation.FeedbackerAi.tools.models.sentiment_analysis.cardiffnlp.twitter_roberta import TwitterRoberta
from innovation.FeedbackerAi.tools.models.feature_extraction.ml6team.keyphrase_extraction_kbir_inspec import KeyphraseExtractionKbirInspec
from innovation.FeedbackerAi.tools.models.text_classification.facebook.bart_mnli import BartMnli as FacebookMNLI
from innovation.FeedbackerAi.tools.models.text_classification.microsoft.deberta_mnli import DebertaMnli as MicrosoftMNLI
from innovation.FeedbackerAi.tools.local.entities.model_type import MODEL_TEXT_TRANSLATION, MODEL_TEXT_CLASSIFICATION, MODEL_TEXT_FEATURE_EXTRACTION, MODEL_TEXT_SUMMARIZATION, MODEL_TEXT_QUESTION_ANSWER, MODEL_TEXT_CONVERSATION, MODEL_VISUAL_ENVIRONMENT, MODEL_VISUAL_OBJECT_DETECTION, MODEL_VISUAL_MOVEMENT, MODEL_VISUAL_CLASSIFICATION, MODEL_TEXT_SENTIMENT_ANALYSIS


class Factory(ABC):
    config = None
    model_to_run = None

    def __init__(self, model_config_name, config, token=None):
        self.model_config_name = model_config_name
        self.config = config
        self.token = token
        for model_to_run in self.config:
            if model_to_run['is_enabled']:
                self.model_to_run = model_to_run

# VISUAL MODELS #

class VisualModelFactory(Factory, ABC):
    @abstractmethod
    def create(self, device, pretrained, to_debug=0):
        pass

class ObjectFactory(VisualModelFactory):

    MODEL_TYPE = MODEL_VISUAL_OBJECT_DETECTION

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, device, pretrained, to_debug=0):
        
        if not self.model_to_run:
            return None

        # do reflection here
        model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        # if ObjectFactory.MODEL_TYPE.MICROSOFT_GLIP.value in self.model_config_name:
        #     return Glip(self.model_to_run, self.token, model_name, device, pretrained, to_debug)
        # if ObjectFactory.MODEL_TYPE.FACEBOOK_DETR.value in self.model_config_name:
        #     return Detr(self.model_to_run, self.token, model_name, device, pretrained, to_debug)
        if ObjectFactory.MODEL_TYPE.OPENAI_CLIP.value in self.model_config_name:
            return Clip(self.model_to_run, self.token, model_name, device, pretrained, to_debug)


class EnvironmentFactory(VisualModelFactory):
    
    MODEL_TYPE = MODEL_VISUAL_ENVIRONMENT

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, device, pretrained, to_debug=0):
        return None

class VisualClassificationFactory(VisualModelFactory):
    
    MODEL_TYPE = MODEL_VISUAL_CLASSIFICATION

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, device, pretrained, to_debug=0):
        if not self.model_to_run:
            return None


class MovementFactory(VisualModelFactory):
    
    MODEL_TYPE = MODEL_VISUAL_MOVEMENT

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, device, pretrained, to_debug=0):
        return None

# TEXT MODELS #

class TextModelFactory(Factory):
    @abstractmethod
    def create(self, pretrained, to_debug=0):
        pass

class ConversationFactory(TextModelFactory, ABC):
    
    MODEL_TYPE = MODEL_TEXT_CONVERSATION
        
    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        if not self.model_to_run:
            return None

        # do reflection here
        # model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        # if ConversationFactory.MODEL_TYPE.OPENAI_GPT2.value in self.model_config_name:
        #     return Gpt2(self.model_to_run, self.token, model_name, pretrained, to_debug)
        # if ConversationFactory.MODEL_TYPE.META_LLAMA_31.value in self.model_config_name:
        #     pass
        
class SentimentAnalysisFactory(TextModelFactory, ABC):
    
    MODEL_TYPE = MODEL_TEXT_SENTIMENT_ANALYSIS
        
    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        if not self.model_to_run:
            return None

        # do reflection here
        model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        if SentimentAnalysisFactory.MODEL_TYPE.CARDIFFNLP_TWITTER_ROBERTA.value in self.model_config_name:
            return TwitterRoberta(self.model_to_run, self.token, model_name, pretrained, to_debug)

class TranslationFactory(TextModelFactory, ABC):
    
    MODEL_TYPE = MODEL_TEXT_TRANSLATION
        
    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        if not self.model_to_run:
            return None

        # do reflection here
        # model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        # if TranslationFactory.MODEL_TYPE.GOOGLE_MT5.value in self.model_config_name:
        #     return Mt5(self.model_to_run, self.token, model_name, pretrained, to_debug)
        # if TranslationFactory.MODEL_TYPE.FACEBOOK_MULTILANG_NLLB.value in self.model_config_name:
        #     return Multilang_Nllb(self.model_to_run, self.token, model_name, pretrained, to_debug)

class SummarizationFactory(TextModelFactory, ABC):
    
    MODEL_TYPE = MODEL_TEXT_SUMMARIZATION
        
    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        if not self.model_to_run:
            return None

        # do reflection here
        # model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        # if SummarizationFactory.MODEL_TYPE.GOOGLE_PEGASUS_XSUM.value in self.model_config_name:
        #     return PegasusXsum(self.model_to_run, self.token, model_name, pretrained, to_debug)
        
class FeatureExtractionFactory(TextModelFactory, ABC):
    
    MODEL_TYPE = MODEL_TEXT_FEATURE_EXTRACTION
        
    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        if not self.model_to_run:
            return None
        
        # do reflection here
        model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        if FeatureExtractionFactory.MODEL_TYPE.ML6TEAM_KEYPHRASE_EXTRACTION.value in self.model_config_name:
            return KeyphraseExtractionKbirInspec(self.model_to_run, self.token, model_name, pretrained, to_debug)

class TextclassificationFactory(TextModelFactory, ABC):
    
    MODEL_TYPE = MODEL_TEXT_CLASSIFICATION
        
    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        if not self.model_to_run:
            return None

        # do reflection here
        model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        if TextclassificationFactory.MODEL_TYPE.FACEBOOK_BART_MNLI.value in self.model_config_name:
            return FacebookMNLI(self.model_to_run, self.token, model_name, pretrained, to_debug)
        if TextclassificationFactory.MODEL_TYPE.MICROSOFT_DEBERTA_MNLI.value in self.model_config_name:
            return MicrosoftMNLI(self.model_to_run, self.token, model_name, pretrained, to_debug)
    
class QuestionAnswerFactory(TextModelFactory):
    
    MODEL_TYPE = MODEL_TEXT_QUESTION_ANSWER

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        
        if not self.model_to_run:
            return None
        
         # do reflection here
        # model_name = self.model_to_run['repository']+"/"+self.model_to_run['name']
        # if QuestionAnswerFactory.MODEL_TYPE.DEEPSET_SQUAD2.value in self.model_config_name:
        #     return Squad2(self.model_to_run, self.token, model_name, pretrained, to_debug)
