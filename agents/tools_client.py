from innovation.FeedbackerAi.tools.local.fallback.donothing.do_nothing import DoNothing
from innovation.FeedbackerAi.tools.local.fallback.userinput.user_input import UserInput
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT
from innovation.FeedbackerAi.tools.sources.source import Source
from innovation.FeedbackerAi.tools.players.player import Player
from innovation.FeedbackerAi.tools.models.model import Model
from innovation.FeedbackerAi.tools.models.client import ModelClient, Translation, TextClassification, ObjectDetection, Conversation, QuestionAnswer, VisualClassification, SentimentAnalysis, Summarization, FeatureExtraction
from innovation.FeedbackerAi.tools.players.client import PlayerClient, GenericPlayer, GamingPlayer
from innovation.FeedbackerAi.tools.sources.client import SourceClient
from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
import innovation.FeedbackerAi.tools.local.entities.source_type as SOURCE_TYPE
from enum import Enum
from typing import Optional, Dict, Any, List

# Make sure the operation order is kept
class Operation(Enum):
    EXTRACT_GENRE = "extract-genre", GENRE
    GET_FEATURES = "get-features" 
    GET_GAMES = "get-games"
    GET_REVIEWS = "get-reviews"
    # DO_TRANSLATION = "do-translation"
    DO_SENTIMENT_ANALYSIS = "do-sentiment-analysis", REVIEW_SENTIMENT
    GET_TRENDS = "get-trends"
    CLASSIFY_TRENDS = "classify-trends"
    DO_SUMMARIZATION = "do-summarization"
    EXTRACT_VIDEO_OBJECT_DETECTION_FEATURES = "extract-video-object-detection-features"
    EXTRACT_VIDEO_ENVIRONMENT_FEATURES = "extract-video-environment-features"
    EXTRACT_VIDEO_MOVEMENT_FEATURES = "extract-video-movement-features"
    
    def __init__(self, description, output_available_options: Enum = None, input: dict = None):
        super().__init__()
        self.description = description
        self.input = input
        self.output_available_options = output_available_options
    
class ComponentType(Enum):
    MODEL = "model"
    SOURCE = "source"
    PLAYER = "player"
    
class ExecutionMode(Enum):
    SKIP = "skip"
    FALLBACK = "fallback"
    MULTIPLE = "multiple"
    SINGLE = "single"

class ToolsFactory(ABC):
    
    def __init__(self, workflow_config, bot_config):
        self.models: Dict = {"components": List[Model], "execution_mode": ExecutionMode} 
        self.sources: Dict = {"components": List[Source], "clients": List[SourceClient], "execution_mode": ExecutionMode} 
        self.player: Dict = {"components": Player, "execution_mode": ExecutionMode}  
        self.workflow_config: dict = workflow_config
        self.bot_config: dict = bot_config
        
    # def __init__(self, model_factory, source_factories, player_factory):
    #     self.model_factory: Model = model_factory
    #     self.source_factories: List[Source] = source_factories
    #     self.player_factory: Player = player_factory
    
    def createModels(self, execution_mode: ExecutionMode = ExecutionMode.SINGLE):
        models_config: str = self.workflow_config['models']

        if not models_config:
            return None, ExecutionMode.SKIP
        
        if not isinstance(models_config, List):
            if models_config.lower() == "none":
                return None, ExecutionMode.SKIP
            elif models_config.lower() == "fallback":
                return None, ExecutionMode.FALLBACK
            else:
                if execution_mode == ExecutionMode.MULTIPLE:
                    raise Exception("Model {models_config} is not available")
        
        if execution_mode == ExecutionMode.SINGLE:
            if isinstance(models_config, List):
                if len(models_config) > 1:
                    raise Exception("This operation only allows 1 model")
        
        if execution_mode == ExecutionMode.MULTIPLE:
            if isinstance(models_config, List):
                if len(models_config) <= 1:
                    raise Exception("This operation is expected to run more than 1 model")
            else:
                raise Exception("This operation is expected to run more than 1 model")
            
        return models_config, execution_mode
        
    def createSources(self, execution_mode: ExecutionMode = ExecutionMode.SINGLE):
        sources_config: str = self.workflow_config['sources']

        if not sources_config:
            return None, ExecutionMode.SKIP
        
        if not isinstance(sources_config, List):
            if sources_config.lower() == "none":
                return None, ExecutionMode.SKIP
            elif sources_config.lower() == "fallback":
                return None, ExecutionMode.FALLBACK
            else:
                if execution_mode == ExecutionMode.MULTIPLE:
                    raise Exception("Source {sources_config} is not available")
        
        if execution_mode == ExecutionMode.SINGLE:
            if isinstance(sources_config, List):
                if len(sources_config) > 1:
                    raise Exception("This operation only allows 1 source")
        
        if execution_mode == ExecutionMode.MULTIPLE:
            if isinstance(sources_config, List):
                if len(sources_config) <= 1:
                    raise Exception("This operation is expected to run more than 1 source")
        
        # NEEDS REFACTORING - creates a lot of dependencies = ENUM needs to match the CLASS name. Reflection is not a good option
        if sources_config:
            sources = []
            for source_config_name in sources_config:
                source_enum = SOURCE_TYPE.recurse_bottom_to_top(source_config_name, number_of_levels=1)
                # client = source_enum.get_client()
                sources.append(source_enum.get_client())
                # source = client.create()
                # sources.append(source)
            return sources, execution_mode
        return sources_config, execution_mode
    
    def createPlayer(self):
        player_config: str = self.workflow_config['player']

        if not player_config:
            return None, ExecutionMode.SKIP
        
        if not isinstance(player_config, List):
            if player_config.lower() == "none":
                return None, ExecutionMode.SKIP
            elif player_config.lower() == "fallback":
                return None, ExecutionMode.FALLBACK
            else:
                raise Exception("Player {player_config} is not available")
        
        return player_config, ExecutionMode.SINGLE
    
class GetGenreFactory(ToolsFactory):
        
    def createModels(self):
        model_config_name, execution_mode = super().createModels()
                    
        model = VisualClassification.create(model_config_name, 
                                            self.bot_config["use_model_finetuned"], 
                                            self.bot_config["device_debug"], 
                                            self.bot_config["device_type"])
        return [model], execution_mode
    
class GetGamesFactory(ToolsFactory):
    
    def createSources(self):
        return super().createSources()
    
class GetReviewsFactory(ToolsFactory):
    
    def createSources(self):
        return super().createSources()

# class DoTranslationFactory(ToolsFactory):
    
#     def createModels(self):
#         model_config_name, execution_mode = super().createModels()
                    
#         model = Translation.create(model_config_name, 
#                                             self.bot_config["use_model_finetuned"], 
#                                             self.bot_config["device_debug"])
#         return [model], execution_mode
        
class DoSentimentAnalysisFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super().createModels()
        
        models = []     
        for model_config_name in model_config_names:
            models.append(SentimentAnalysis.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, execution_mode
    
class GetTrendsFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super().createModels()
        
        models = []     
        for model_config_name in model_config_names:
            models.append(FeatureExtraction.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, execution_mode
    
class ClassifyTrendsFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super().createModels(ExecutionMode.MULTIPLE)
        
        models = []     
        for model_config_name in model_config_names:
            models.append(TextClassification.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, execution_mode
    
class ExtractObjectFeaturesFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super().createModels()
        
        models = []     
        for model_config_name in model_config_names:
            models.append(ObjectDetection.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"], 
                                                self.bot_config["device_type"]))
        return models, execution_mode
    
class ToolsClient:
    
    def __init__(self, workflow_config, bot_config):
        self.workflow_config = workflow_config
        self.bot_config = bot_config

    def create(self, bot_operation: Operation):
        
        bot_operation_str = bot_operation.description
        workflow_config_operation = self.workflow_config[bot_operation_str]
        
        # ADD ALL STEPS DONE BY THE BOT
        print(f"--- {bot_operation_str} ---")
        if bot_operation == Operation.EXTRACT_GENRE:
            factory = GetGenreFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_GAMES:
            factory = GetGamesFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_REVIEWS:
            factory = GetReviewsFactory(workflow_config_operation, self.bot_config)
        # elif bot_operation == Operation.DO_TRANSLATION:
        #     factory = DoTranslationFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.DO_SENTIMENT_ANALYSIS:
            factory = DoSentimentAnalysisFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_TRENDS:
            factory = GetTrendsFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.CLASSIFY_TRENDS:
            factory = ClassifyTrendsFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.EXTRACT_VIDEO_OBJECT_DETECTION_FEATURES:
            factory = ExtractObjectFeaturesFactory(workflow_config_operation, self.bot_config)          
        else:
            raise Exception(f"{bot_operation_str} has not been implement nor exists.")
        
        models, execution_mode_models = factory.createModels()
        sourcesClients, execution_mode_sources = factory.createSources()
        player, execution_mode_player = factory.createPlayer()
        
        if execution_mode_models == ExecutionMode.FALLBACK:
            models = [UserInput(bot_operation)]
        if execution_mode_models == ExecutionMode.SKIP:
            models = [DoNothing()]
            
        sources = []
        if execution_mode_sources == ExecutionMode.FALLBACK:
            sources = [UserInput(bot_operation)]
        if execution_mode_sources == ExecutionMode.SKIP:
            sources = [DoNothing()] 
            
        if execution_mode_player == ExecutionMode.FALLBACK:
            player = UserInput(bot_operation)
        if execution_mode_player == ExecutionMode.SKIP:
            player = DoNothing()
            
        self.models = {"components": models, "execution_mode": execution_mode_models}
        self.sources = {"components": [sourceClient.create() for sourceClient in sourcesClients] if not sources else sources, "clients": sourcesClients, "execution_mode": execution_mode_sources}
        self.player = {"components": player, "execution_mode": execution_mode_player}
        
        return self.models, self.sources, self.player