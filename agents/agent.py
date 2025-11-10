from abc import ABC
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.agents.tools_client import ToolsClient, ExecutionMode, ComponentType, Operation
from innovation.FeedbackerAi.agents.entities.question import Question
from innovation.FeedbackerAi.agents.entities.answer import Answer
from typing import Optional, Dict, Any, List, Set

class Agent(ABC):   
    
    components = []
    executionMode = None
    
    def __init__(self, workflow_config, bot_config):
        self.tools_client = ToolsClient(workflow_config, bot_config)
        
    def to_fallback(operation_type: Operation, component_type: ComponentType):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                # Create the specified operation
                models, sources, player = self.tools_client.create(operation_type)
                
                if component_type == ComponentType.MODEL:
                    self.executionMode = models["execution_mode"]
                    self.components = models["components"]
                if component_type == ComponentType.SOURCE:
                    self.executionMode = sources["execution_mode"]
                    self.components = sources["clients"]
                if component_type == ComponentType.PLAYER:
                    self.executionMode = player["execution_mode"]
                    self.components = player["components"]
                
                # Check for models availability
                if not self.components:
                    return None

                # Run the model based on execution mode
                if self.executionMode == ExecutionMode.FALLBACK:
                    return self.components[0].execute()

                # Proceed with the wrapped function if needed
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
        
    def concatenate_fn(self, question: Question) -> Set[Answer]:
        """
        Concatenates answers from multiple components by executing a question on each.

        Args:
            components (list): A list of components, that can be models, sources or players
            question: The question to be executed on each component.

        Returns:
            list: A merged list containing all answers from all components.
        """
        results = list()
        for component in self.components:
            answers: Set[Answer] = component.execute(question)
            
            if not answers:
                continue
            
            results.extend(answers)
        return results
    
    def concatenate_fn(self, question: Question) -> Set[Answer]:
        """
        Concatenates answers from multiple components by executing a question on each.

        Args:
            components (list): A list of components, that can be models, sources or players
            question: The question to be executed on each component.

        Returns:
            list: A merged list containing all answers from all components.
        """
        results = list()
        for component in self.components:
            answers: Set[Answer] = component.execute(question)
            
            if not answers:
                continue
            
            results.extend(answers)
        return results

    def intersect_fn(self, question: Question, param_match_index=0, param_max_index=1) -> Set[Answer]:
        """
        Performs an intersection of answers from multiple components based on specified tuple indices,
        filtering results to those with maximum values at a given index.

        Args:
            components (list): A list of components that can be models, sources or players
            question: The question to be executed on each component.
            param_match_index (int, optional): Index within answer tuples to use as the matcher between 2 lists. Defaults to 0.
            param_max_index (int, optional): Index within answer tuples to find the best score. Defaults to 1.

        Returns:
            list: A list of tuples representing the intersected and filtered answers based on the highest score
        """
        filtered_results = []
        confidence_threshold_model = None

        for component in self.components:
            answers: Set[Answer] = component.execute(question)

            if not answers:
                continue
            
            for answer in answers:
                if not confidence_threshold_model:
                    confidence_threshold_model = float(answer.score)
            
            if not filtered_results:
                filtered_results.extend(answers)
                continue
                
            filtered_results = set(Utility.get_list_tuples_with_max_value(answers, filtered_results, param_match_index, param_max_index))
                
        return filtered_results
        
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