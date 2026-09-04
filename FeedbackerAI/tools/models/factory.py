from abc import ABC, abstractmethod
from tools.models.object.glip.glip import Glip
from tools.models.object.detr.detr import Detr
from tools.models.model import Model
from tools.models.fallback.userinput.user_input import UserInput
from tools.models.fallback.donothing.do_nothing import DoNothing
from enum import Enum


class Factory(ABC):
    config = None

    def __init__(self, config, token=None):
        self.config = config
        self.token = token

    @abstractmethod
    def create(self, device, pretrained, to_debug=0):
        pass

    def to_fallback(self, model_to_replace, topic=""):
        if not self.config:
            return DoNothing()
        for model_to_run in self.config:
            if model_to_run['is_enabled']:
                return model_to_run
        return UserInput(model_to_replace, topic)


class ObjectFactory(Factory):

    class ModelType(Enum):
        MICROSOFT_GLIP = 'glip'
        FACEBOOK_DETR = 'detr'

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


class EnvironmentFactory(Factory):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        return None


class VideoClassificationFactory(Factory):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        model_to_run = super().to_fallback("Video Classification")
        if isinstance(model_to_run, Model):
            return model_to_run

        # do reflection here
        return None


class MovementFactory(Factory):

    def __init__(self, config, token=None):
        super().__init__(config, token)

    def create(self, device, pretrained, to_debug=0):
        return None
