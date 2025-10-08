from abc import ABC, abstractmethod
from tools.models.object.microsoft.glip import Glip
from tools.models.object.facebook.detr import Detr
from tools.models.object.openai.clip import Clip
from tools.models.question_answer.deepset.squad2 import Squad2
from tools.models.model import Model
from tools.models.fallback.userinput.user_input import UserInput
from tools.models.fallback.donothing.do_nothing import DoNothing
from enum import Enum


class Factory(ABC):
    config = None

    def __init__(self, config, token=None):
        self.config = config
        self.token = token

    def to_fallback(self, model_to_replace, topic=""):
        if not self.config:
            return DoNothing()
        for model_to_run in self.config:
            if model_to_run['is_enabled']:
                return model_to_run
        return UserInput(model_to_replace, topic)

# VIDEO MODELS #

class VideoModelFactory(Factory, ABC):
    @abstractmethod
    def create(self, device, pretrained, to_debug=0):
        pass

class ObjectFactory(VideoModelFactory):

    class ModelType(Enum):
        MICROSOFT_GLIP = 'glip'
        FACEBOOK_DETR = 'detr'
        OPENAI_CLIP = 'clip'

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        model_to_run = super().to_fallback("Object Detection")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
        model_name = model_to_run['repository']+"/"+model_to_run['name']
        if ObjectFactory.ModelType.MICROSOFT_GLIP.value in model_name.lower():
            return Glip(model_to_run, self.token, model_name, device, pretrained, to_debug)
        if ObjectFactory.ModelType.FACEBOOK_DETR.value in model_name.lower():
            return Detr(model_to_run, self.token, model_name, device, pretrained, to_debug)
        if ObjectFactory.ModelType.OPENAI_CLIP.value in model_name.lower():
            return Clip(model_to_run, self.token, model_name, device, pretrained, to_debug)


class EnvironmentFactory(VideoModelFactory):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        return None


class VideoClassificationFactory(VideoModelFactory):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        model_to_run = super().to_fallback("Video Classification")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
        return None


class MovementFactory(VideoModelFactory):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        return None

# TEXT MODELS #

class TextModelFactory(Factory):
    @abstractmethod
    def create(self, pretrained, to_debug=0):
        pass

class ConversationFactory(TextModelFactory, ABC):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, pretrained, to_debug=0):
        model_to_run = super().to_fallback("Conversation")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
        return None
    
class QuestionAnswerFactory(TextModelFactory):
    
    class ModelType(Enum):
        DEEPSET_SQUAD2 = 'squad2'

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, pretrained, to_debug=0):
        
        model_to_run = super().to_fallback("Question-Answer")
        if isinstance(model_to_run, Model):
            return model_to_run
        
         # do reflection here
        model_name = model_to_run['repository']+"/"+model_to_run['name']
        if QuestionAnswerFactory.ModelType.DEEPSET_SQUAD2.value in model_name.lower():
            return Squad2(model_to_run, self.token, model_name, pretrained, to_debug)
