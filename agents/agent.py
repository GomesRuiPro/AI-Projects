from abc import ABC
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.agents.tools_client import ToolsClient
from typing import Optional, Dict, Any

class Agent(ABC):
    
    # models: Dict[str, Any] = {}
    # sources: Dict[str, Any] = {}
    # player = None
    
    def __init__(self, workflow_config, bot_config):
        self.tools_client = ToolsClient(workflow_config, bot_config)
        
    # Something for the future - dynamically decide which models will be executed from the config.yml file
    
    # def start_model(self, models_config: dict):
    #     for model_config in models_config.items():
    #         Utility.find_maps_with_key
    #         if model_config.value == "none":
    #             self.models[model_config] = None
    #         if 

    # def get_model(self, model_type):
    #     return self.models[model_type]

    # def get_models(self):
    #     return self.models
    
    # def get_source(self, source_type):
    #     return self.sources[source_type]

    # def get_sources(self):
    #     return self.sources
    
    # def get_player(self):
    #     return self.player