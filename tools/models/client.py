from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.models.factory import ConversationFactory, QuestionAnswerFactory
from innovation.FeedbackerAi.tools.models.factory import EnvironmentFactory, MovementFactory, VideoClassificationFactory, ObjectFactory

MODELS_CONFIG = Utility.load_yaml()["models"]

class ModelClient(ABC):

    model = None

    @abstractmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        pass

# TEXT MODELS #
class Conversation(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['conversation']
        conversationFactory = ConversationFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        ModelClient.model = conversationFactory.create(
            use_model_finetuned, device_debug)
        return ModelClient.model

class QuestionAnswer(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['question_answer']
        questionAnswerFactory = QuestionAnswerFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        ModelClient.model = questionAnswerFactory.create(
            use_model_finetuned, device_debug)
        return ModelClient.model    
    
# VISUAL MODELS #
class VisualModelClient(ModelClient, ABC):

    @abstractmethod
    def create(model_config_name, use_model_finetuned, device_debug, device_type):
        pass
    
class Movement(VisualModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['movement']


class ObjectDetection(VisualModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug, device_type):
        config = MODELS_CONFIG['object']
        objectFactory = ObjectFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        ModelClient.model = objectFactory.create(
            device_type, use_model_finetuned, device_debug)
        return ModelClient.model


class Environment(VisualModelClient):

    @staticmethod
    def create(use_model_finetuned, device_debug, device_type):
        config = MODELS_CONFIG['environment']


class VideoClassification(VisualModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug, device_type):
        config = MODELS_CONFIG['video_classification']
        videoClassificationFactory = VideoClassificationFactory(model_config_name, config)
        ModelClient.model = videoClassificationFactory.create(
            device_type, use_model_finetuned, device_debug)
        return ModelClient.model
