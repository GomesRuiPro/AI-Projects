from abc import ABC
from innovation.FeedbackerAi.tools.utilities import Utility

class Agent(ABC):
    
    models = {}
    
    def __init__(self):
        pass
        
    # Something for the future - dynamically decide which models will be executed from the config.yml file
    
    # def start_model(self, models_config: dict):
    #     for model_config in models_config.items():
    #         Utility.find_maps_with_key
    #         if model_config.value == "none":
    #             self.models[model_config] = None
    #         if 

    def get_model(self, model_type):
        return self.models[model_type]

    def get_models(self):
        return self.models