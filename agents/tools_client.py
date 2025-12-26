from innovation.FeedbackerAi.tools.fallback.donothing.do_nothing import DoNothing
from innovation.FeedbackerAi.tools.fallback.user_input import UserInput
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT
from innovation.FeedbackerAi.tools.sources.source import Source
from innovation.FeedbackerAi.tools.players.player import Player
from innovation.FeedbackerAi.tools.models.model import Model
from innovation.FeedbackerAi.tools.models.client import VideoFeatureExtraction, ModelClient, Translation, TextClassification, Conversation, QuestionAnswer, VisualClassification, SentimentAnalysis, Summarization, TextFeatureExtraction
from innovation.FeedbackerAi.tools.players.client import PlayerClient, GenericPlayer, GamingPlayer
from innovation.FeedbackerAi.tools.sources.client import SourceClient
from innovation.FeedbackerAi.tools.fallback.console.console import ConsoleInput
from innovation.FeedbackerAi.tools.fallback.file.file import JsonInput
from abc import ABC, abstractmethod
from innovation.FeedbackerAi.tools.local.utilities import Utility
import innovation.FeedbackerAi.tools.local.entities.source_type as SOURCE_TYPE
import innovation.FeedbackerAi.tools.local.entities.model_type as MODEL_VISUAL
from enum import Enum
from typing import Optional, Dict, Any, List

# Make sure the operation order is kept
class Operation(Enum):
    EXTRACT_GENRE = "extract-genre", GENRE # In case of fallback, you can use the available options
    GET_GAMES = "get-games"
    GET_REVIEWS = "get-reviews"
    # DO_TRANSLATION = "do-translation"
    DO_SENTIMENT_ANALYSIS = "do-sentiment-analysis", REVIEW_SENTIMENT
    GET_TRENDS = "get-trends"
    CLASSIFY_TRENDS = "classify-trends"
    DO_SUMMARIZATION = "do-summarization"
    EXTRACT_VIDEO_FEATURES = "extract-video-features"
    CREATE_FEEDBACK_REPORT = "create-feedback-report"
    
    def __init__(self, description, output_available_options: Enum = None, input: dict = None, is_multiple_answers_allowed=False):
        super().__init__()
        self.description = description
        self.input = input
        self.output_available_options = output_available_options
        self.is_multiple_answers_allowed = is_multiple_answers_allowed
    
class ExecutionMode(Enum):
    SKIP = "skip" 
    FALLBACK = "fallback"
    MULTIPLE = "multiple" # Forces the use of more than 1 component
    SINGLE = "single" # Forces the use of only 1 component
    UNKNOWN = "unknown" # Default behavior: it accepts any number of components to run

class ToolsFactory(ABC):
    
    def __init__(self, workflow_config, bot_config):
        self.models: Dict = {"components": List[Model], "clients": List[ModelClient], "execution_mode": ExecutionMode} 
        self.sources: Dict = {"components": List[Source], "clients": List[SourceClient], "execution_mode": ExecutionMode} 
        self.player: Dict = {"components": Player, "clients": PlayerClient, "execution_mode": ExecutionMode}  
        self.workflow_config: dict = workflow_config
        self.bot_config: dict = bot_config
        
    # def __init__(self, model_factory, source_factories, player_factory):
    #     self.model_factory: Model = model_factory
    #     self.source_factories: List[Source] = source_factories
    #     self.player_factory: Player = player_factory
    
    @abstractmethod
    def createModels(self):
        pass
    @abstractmethod
    def createSources(self):
        pass
    @abstractmethod
    def createPlayer(self):
        pass
    
    def _createModels(self, execution_mode: ExecutionMode = ExecutionMode.UNKNOWN):
        models_config: str = self.workflow_config['models']

        if not models_config:
            return [], ExecutionMode.SKIP
        
        if not isinstance(models_config, List):
            if models_config.lower() == "none":
                return [], ExecutionMode.SKIP
            elif models_config.lower() == "fallback":
                return [], ExecutionMode.FALLBACK
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
        
    def _createSources(self, execution_mode: ExecutionMode = ExecutionMode.SINGLE):
        sources_config: str = self.workflow_config['sources']

        if not sources_config:
            return [], ExecutionMode.SKIP
        
        if not isinstance(sources_config, List):
            if sources_config.lower() == "none":
                return [], ExecutionMode.SKIP
            elif sources_config.lower() == "fallback":
                return [], ExecutionMode.FALLBACK
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
        
        return sources_config, execution_mode

    def _createSourcesClients(self, sources_config_names):
        # NEEDS REFACTORING - creates a lot of dependencies = ENUM needs to match the CLASS name. Reflection is not a good option
        sourcesClients = []
        if sources_config_names:
            for source_config_name in sources_config_names:
                source_enum = SOURCE_TYPE.recurse_bottom_to_top(source_config_name, number_of_levels=1)
                sourcesClients.append(source_enum.get_client())
        return sourcesClients
    
    def _createPlayer(self):
        player_config: str = self.workflow_config['player']

        if not player_config:
            return [], ExecutionMode.SKIP
        
        if not isinstance(player_config, List):
            if player_config.lower() == "none":
                return [], ExecutionMode.SKIP
            elif player_config.lower() == "fallback":
                return [], ExecutionMode.FALLBACK
            else:
                raise Exception("Player {player_config} is not available")
        
        return player_config, ExecutionMode.SINGLE
    
class GetGenreFactory(ToolsFactory):
        
    def createModels(self):
        model_config_name, execution_mode = super()._createModels(ExecutionMode.SINGLE)
                    
        client = VisualClassification
        model = client.create(model_config_name, 
                                            self.bot_config["use_model_finetuned"], 
                                            self.bot_config["device_debug"], 
                                            self.bot_config["device_type"])
        return [model], [client], execution_mode
    
    def createSources(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
    
class GetGamesFactory(ToolsFactory):
    
    def createSources(self):
        sources_config_names, execution_mode = super()._createSources()
        sourcesClients = super()._createSourcesClients(sources_config_names)
        sources = [sourceClient.create() for sourceClient in sourcesClients]
        return sources, sourcesClients, execution_mode
    
    def createModels(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP

    
class GetReviewsFactory(ToolsFactory):
    
    def createSources(self):
        sources_config_names, execution_mode = super()._createSources()
        sourcesClients = super()._createSourcesClients(sources_config_names)
        sources = [sourceClient.create() for sourceClient in sourcesClients]
        return sources, sourcesClients, execution_mode
    
    def createModels(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
        
class DoSentimentAnalysisFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super()._createModels()
        
        models = []     
        client = SentimentAnalysis
        
        for model_config_name in model_config_names:
            models.append(client.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, [client], execution_mode
    
    def createSources(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
    
class GetTrendsFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super()._createModels()
        
        models = []     
        client = TextFeatureExtraction
        for model_config_name in model_config_names:
            models.append(client.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, [client], execution_mode
    
    def createSources(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
    
class ClassifyTrendsFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super()._createModels()
        
        client = TextFeatureExtraction
        models = []     
        for model_config_name in model_config_names:
            models.append(client.create(model_config_name, 
                                                self.bot_config["use_model_finetuned"], 
                                                self.bot_config["device_debug"]))
        return models, [client], execution_mode
    
    def createSources(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
    
class ExtractVideoFeaturesFactory(ToolsFactory):
    def createModels(self):
        model_config_names, execution_mode = super()._createModels()
        
        models = []
        clients = [VideoFeatureExtraction, VisualClassification]
        for client in clients:
            for model_config_name in model_config_names:
                models.append(client.create(model_config_name, 
                                                    self.bot_config["use_model_finetuned"], 
                                                    self.bot_config["device_debug"], 
                                                    self.bot_config["device_type"]))
        
        return models, [client], execution_mode
    
    def createSources(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
    
class CreateFeedbackReport(ToolsFactory):
    def createModels(self):
        return [], [], ExecutionMode.SKIP
    
    def createSources(self):
        return [], [], ExecutionMode.SKIP
    
    def createPlayer(self):
        return None, None, ExecutionMode.SKIP
    
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
        elif bot_operation == Operation.DO_SENTIMENT_ANALYSIS:
            factory = DoSentimentAnalysisFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.GET_TRENDS:
            factory = GetTrendsFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.CLASSIFY_TRENDS:
            factory = ClassifyTrendsFactory(workflow_config_operation, self.bot_config)
        elif bot_operation == Operation.EXTRACT_VIDEO_FEATURES:
            factory = ExtractVideoFeaturesFactory(workflow_config_operation, self.bot_config)          
        elif bot_operation == Operation.CREATE_FEEDBACK_REPORT:
            factory = CreateFeedbackReport(workflow_config_operation, self.bot_config) 
        else:
            raise Exception(f"{bot_operation_str} has not been implement nor exists.")
        
        models, modelsClients, execution_mode_models = factory.createModels()
        sources, sourcesClients, execution_mode_sources = factory.createSources()
        player, playerClient, execution_mode_player = factory.createPlayer()
        
        if execution_mode_models == ExecutionMode.FALLBACK:
            models = [self.decide_user_input(bot_operation)]
        if execution_mode_models == ExecutionMode.SKIP:
            models = [DoNothing()]
            
        if execution_mode_sources == ExecutionMode.FALLBACK:
            sources = [self.decide_user_input(bot_operation)]
        if execution_mode_sources == ExecutionMode.SKIP:
            sources = [DoNothing()] 
            
        if execution_mode_player == ExecutionMode.FALLBACK:
            player = self.decide_user_input(bot_operation)
        if execution_mode_player == ExecutionMode.SKIP:
            player = DoNothing()
            
        self.models = {"components": [model for model in models if model], "clients": modelsClients, "execution_mode": execution_mode_models}
        self.sources = {"components": [source for source in sources if source], "clients": sourcesClients, "execution_mode": execution_mode_sources}
        self.player = {"components": player, "clients": playerClient, "execution_mode": execution_mode_player}
        
        return self.models, self.sources, self.player
    
    def decide_user_input(self, bot_operation: Operation):
        if bot_operation.output_available_options:
            return ConsoleInput(bot_operation)
        return JsonInput(bot_operation)