from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.models.object.microsoft.glip import Glip
from innovation.FeedbackerAi.tools.models.object.facebook.detr import Detr
from innovation.FeedbackerAi.tools.models.object.openai.clip import Clip
from innovation.FeedbackerAi.tools.models.question_answer.deepset.squad2 import Squad2
from innovation.FeedbackerAi.tools.models.conversation.openai.gpt2 import Gpt2
from innovation.FeedbackerAi.tools.models.model import Model
from innovation.FeedbackerAi.tools.models.fallback.userinput.user_input import UserInput
from innovation.FeedbackerAi.tools.models.fallback.donothing.do_nothing import DoNothing
from innovation.FeedbackerAi.tools.local.entities.model_type import MODEL_TEXT_QUESTION_ANSWER, MODEL_TEXT_CONVERSATION, MODEL_VISUAL_ENVIRONMENT, MODEL_VISUAL_OBJECT_DETECTION, MODEL_VISUAL_MOVEMENT, MODEL_VIDEO_CLASSIFICATION


class Factory(ABC):
    config = None

    def __init__(self, model_config_name, config, token=None):
        self.model_config_name = model_config_name
        self.config = config
        self.token = token

    def to_fallback(self, model_to_replace, topic=""):
        if not self.config:
            return DoNothing()
        for model_to_run in self.config:
            if model_to_run['is_enabled']:
                return model_to_run
        return UserInput(model_to_replace, topic)

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
        model_to_run = super().to_fallback("Object Detection")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
        model_name = model_to_run['repository']+"/"+model_to_run['name']
        if ObjectFactory.MODEL_TYPE.MICROSOFT_GLIP.value == self.model_config_name:
            return Glip(model_to_run, self.token, model_name, device, pretrained, to_debug)
        if ObjectFactory.MODEL_TYPE.FACEBOOK_DETR.value == self.model_config_name:
            return Detr(model_to_run, self.token, model_name, device, pretrained, to_debug)
        if ObjectFactory.MODEL_TYPE.OPENAI_CLIP.value == self.model_config_name:
            return Clip(model_to_run, self.token, model_name, device, pretrained, to_debug)


class EnvironmentFactory(VisualModelFactory):
    
    MODEL_TYPE = MODEL_VISUAL_ENVIRONMENT

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, device, pretrained, to_debug=0):
        return None


class VideoClassificationFactory(VisualModelFactory):
    
    MODEL_TYPE = MODEL_VIDEO_CLASSIFICATION

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, device, pretrained, to_debug=0):
        model_to_run = super().to_fallback("Video Classification")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
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
        model_to_run = super().to_fallback("Conversation")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
        model_name = model_to_run['repository']+"/"+model_to_run['name']
        if ConversationFactory.MODEL_TYPE.OPENAI_GPT2.value == self.model_config_name:
            return Gpt2(model_to_run, self.token, model_name, pretrained, to_debug)
        if ConversationFactory.MODEL_TYPE.META_LLAMA_31.value == self.model_config_name:
            pass
    
class QuestionAnswerFactory(TextModelFactory):
    
    MODEL_TYPE = MODEL_TEXT_QUESTION_ANSWER

    def __init__(self, model_config_name, config, token=None):
        super().__init__(model_config_name, config, token)

    def create(self, pretrained, to_debug=0):
        
        model_to_run = super().to_fallback("Question-Answer")
        if isinstance(model_to_run, Model):
            return model_to_run
        
         # do reflection here
        model_name = model_to_run['repository']+"/"+model_to_run['name']
        if QuestionAnswerFactory.MODEL_TYPE.DEEPSET_SQUAD2.value == self.model_config_name:
            return Squad2(model_to_run, self.token, model_name, pretrained, to_debug)
