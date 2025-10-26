from innovation.FeedbackerAi.tools.models.fallback.donothing.do_nothing import DoNothing as ModelDoNothing
from innovation.FeedbackerAi.tools.models.fallback.userinput.user_input import UserInput as ModelUserInput
from innovation.FeedbackerAi.tools.sources.fallback.donothing.do_nothing import DoNothing as SourceDoNothing
from innovation.FeedbackerAi.tools.sources.fallback.userinput.user_input import UserInput as SourceUserInput
from innovation.FeedbackerAi.tools.players.fallback.donothing.do_nothing import DoNothing as PlayerDoNothing
from innovation.FeedbackerAi.tools.players.fallback.userinput.user_input import UserInput as PlayerUserInput
from innovation.FeedbackerAi.tools.sources.source import Source
from innovation.FeedbackerAi.tools.players.player import Player
from innovation.FeedbackerAi.tools.models.model import Model
from innovation.FeedbackerAi.tools.models.client import ModelClient, Conversation, QuestionAnswer, VideoClassification, SentimentAnalysis, Summarization, FeatureExtraction
from innovation.FeedbackerAi.tools.players.client import PlayerClient, GenericPlayer, GamingPlayer
from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
import innovation.FeedbackerAi.tools.local.entities.source_type as SOURCE_TYPE
from enum import Enum
from typing import Optional, Dict, Any, List

# Make sure the operation order is kept
class Operation:
    EXTRACT_GENRE = "extract-genre"
    GET_FEATURES = "get-features"
    GET_GAMES = "get-games"
    GET_REVIEWS = "get-reviews"
    DO_SENTIMENT_ANALYSIS = "do-sentiment-analysis"
    GET_KEYWORDS = "get-keywords"
    DO_SUMMARIZATION = "do-summarization"
    EXTRACT_VIDEO_OBJECT_DETECTION_FEATURES = "extract-video-object-detection-features"
    EXTRACT_VIDEO_ENVIRONMENT_FEATURES = "extract-video-environment-features"
    EXTRACT_VIDEO_MOVEMENT_FEATURES = "extract-video-movement-features"
    
class ExecutionMode:
    SKIP = "skip"
    FALLBACK = "fallback"
    MULTIPLE = "multiple"
    SINGLE = "single"

class ToolsFactory(ABC):
    
    def __init__(self, workflow_config, bot_config):
        self.models: Dict = {"entitites": List[Model], "execution_mode": ExecutionMode} 
        self.sources: Dict = {"entitites": List[Source], "execution_mode": ExecutionMode} 
        self.player: Dict = {"entitites": Player, "execution_mode": ExecutionMode}  
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
                raise Exception("Model {models_config} is not available")
        
        if execution_mode == ExecutionMode.SINGLE and len(models_config) > 1:
            raise Exception("This operation only allows 1 model")
        
        if execution_mode == ExecutionMode.MULTIPLE and len(models_config) <= 1:
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
                raise Exception("Source {sources_config} is not available")
        
        if execution_mode == ExecutionMode.SINGLE and len(sources_config) > 1:
            raise Exception("This operation only allows 1 model")
        
        if execution_mode == ExecutionMode.MULTIPLE and len(sources_config) <= 1:
            raise Exception("This operation is expected to run more than 1 model")
        
        # NEEDS REFACTORING - creates a lot of dependencies = ENUM needs to match the CLASS name. Reflection is not a good option
        if sources_config:
            sources = []
            for source_config_name in sources_config:
                source_enum = SOURCE_TYPE.recurse_bottom_to_top(source_config_name, number_of_levels=1)
                client = source_enum.get_client()
                source = client.create()
                sources.append(source)
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
        model_config_names, execution_mode = super().createModels()
                    
        model = VideoClassification.create(model_config_names, 
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
        
class DoSentimentAnalysisFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super().createModels()
        
        models = []     
        for model_config_name in model_config_names:
            models.append(SentimentAnalysis.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, execution_mode
    
class GetKeywordsFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super().createModels()
        
        models = []     
        for model_config_name in model_config_names:
            models.append(FeatureExtraction.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, execution_mode
    
class ToolsClient:
    
    def __init__(self, workflow_config, bot_config):
        self.workflow_config = workflow_config
        self.bot_config = bot_config

    def create(self, bot_operation: str):
        
        workflow_config_operation = self.workflow_config[bot_operation]
        
        # ADD ALL STEPS DONE BY THE BOT
        if bot_operation == Operation.EXTRACT_GENRE:
            factory = GetGenreFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_GAMES:
            factory = GetGamesFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_REVIEWS:
            factory = GetReviewsFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.DO_SENTIMENT_ANALYSIS:
            factory = DoSentimentAnalysisFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_KEYWORDS:
            factory = GetKeywordsFactory(workflow_config_operation, self.bot_config)
        else:
            raise Exception(f"{bot_operation.name} has not been implement nor exists.")

        models, execution_mode_models = factory.createModels()
        sources, execution_mode_sources = factory.createSources()
        player, execution_mode_player = factory.createPlayer()
        
        if execution_mode_models == ExecutionMode.FALLBACK:
            models = [ModelUserInput(bot_operation)]
        if execution_mode_models == ExecutionMode.SKIP:
            models = [ModelDoNothing()]
            
        if execution_mode_sources == ExecutionMode.FALLBACK:
            sources = [SourceUserInput(bot_operation)]
        if execution_mode_sources == ExecutionMode.SKIP:
            sources = [SourceDoNothing()] 
            
        if execution_mode_player == ExecutionMode.FALLBACK:
            player = PlayerUserInput(bot_operation)
        if execution_mode_player == ExecutionMode.SKIP:
            player = PlayerDoNothing()
            
        self.models = {"entities": models, "execution_mode": execution_mode_models}
        self.sources = {"entities": sources, "execution_mode": execution_mode_sources}
        self.player = {"entities": player, "execution_mode": execution_mode_player}
        
        return models, sources, player