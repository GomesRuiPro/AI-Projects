from abc import ABC, abstractmethod
from inspect import ismethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.models.entities.model import ModelData, ModelQuestion
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType
from typing import Set, List
from innovation.FeedbackerAi.tools.models.model import Model
from innovation.FeedbackerAi.tools.models.factory import ConversationFactory, QuestionAnswerFactory
from innovation.FeedbackerAi.tools.models.factory import TranslationFactory, TextclassificationFactory, FeatureExtractionFactory, SummarizationFactory, EnvironmentFactory, MovementFactory, VisualClassificationFactory, ObjectFactory, SentimentAnalysisFactory
from innovation.FeedbackerAi.tools.local.entities.model_type import MODEL_VISUAL_FEATURE_EXTRACTION


MODELS_CONFIG = Utility.load_yaml()["models"]

class ModelClient(ABC):

    component_type = ComponentType.MODEL

    @abstractmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        pass
    
    # To select which method to call after intersect / concatenate ops
    @staticmethod
    def execute(model, question: ModelQuestion, method_fn: ismethod, max_results=None) -> List[Answer]:
        return method_fn(model, question, max_results)
    
    @staticmethod
    def run_model(model, modelQuestion: ModelQuestion, max_results=None):
        return model.execute(modelQuestion, max_results)

# TEXT MODELS #
class Conversation(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['conversation']
        conversationFactory = ConversationFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return conversationFactory.create(
            use_model_finetuned, device_debug)

class QuestionAnswer(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['question_answer']
        questionAnswerFactory = QuestionAnswerFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return questionAnswerFactory.create(
            use_model_finetuned, device_debug)
          

class Translation(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['translation']
        translationFactory = TranslationFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return translationFactory.create(
            use_model_finetuned, device_debug)
    
class SentimentAnalysis(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['sentiment_analysis']
        sentimentAnalysisFactory = SentimentAnalysisFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return sentimentAnalysisFactory.create(
            use_model_finetuned, device_debug)
          

class Summarization(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['summarization']
        summarizationFactory = SummarizationFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return summarizationFactory.create(
            use_model_finetuned, device_debug)
          
    
class TextFeatureExtraction(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['text_feature_extraction']
        featureExtractionFactory = FeatureExtractionFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return featureExtractionFactory.create(
            use_model_finetuned, device_debug)
          
    
class TextClassification(ModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug):
        config = MODELS_CONFIG['text_classification']
        textclassificationFactory = TextclassificationFactory(model_config_name,
            config, MODELS_CONFIG['hugging_face_token'])
        return textclassificationFactory.create(
            use_model_finetuned, device_debug)
         
    
# VISUAL MODELS #
class VisualModelClient(ModelClient, ABC):

    @abstractmethod
    def create(model_config_name, use_model_finetuned, device_debug, device_type):
        pass

class VisualClassification(VisualModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug, device_type):
        config = MODELS_CONFIG['video_classification']
        visualClassificationFactory = VisualClassificationFactory(model_config_name, config)
        return visualClassificationFactory.create(
            device_type, use_model_finetuned, device_debug)
        
class VideoFeatureExtraction(VisualModelClient):

    @staticmethod
    def create(model_config_name, use_model_finetuned, device_debug, device_type):
        config = MODELS_CONFIG['video_feature_extraction']
        
        model = None
        for model_type in MODEL_VISUAL_FEATURE_EXTRACTION:
            if model_type == MODEL_VISUAL_FEATURE_EXTRACTION.ENVIRONMENT:
                VideoFeatureExtraction = EnvironmentFactory(model_config_name, config['environment'], MODELS_CONFIG['hugging_face_token'])
            elif model_type == MODEL_VISUAL_FEATURE_EXTRACTION.MOVEMENT:
                VideoFeatureExtraction = MovementFactory(model_config_name, config['movement'], MODELS_CONFIG['hugging_face_token'])
            elif model_type == MODEL_VISUAL_FEATURE_EXTRACTION.OBJECT_DETECTION:
                VideoFeatureExtraction = ObjectFactory(model_config_name, config['object'], MODELS_CONFIG['hugging_face_token'])
            elif model_type == MODEL_VISUAL_FEATURE_EXTRACTION.UNKNOWN:
                continue
            else:
                raise Exception("No visual model was found!")
            
            model = VideoFeatureExtraction.create(device_type, use_model_finetuned, device_debug)
            
            if model:
                break
        
        return model
