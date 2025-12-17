from abc import ABC
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.agents.tools_client import ToolsClient, ExecutionMode, Operation
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.agents.entities.component import Answer
from typing import Optional, Dict, Any, List, Set
import math

class Agent(ABC):   
    
    components = []
    clients = []
    executionMode = None
    
    def __init__(self, workflow_config, bot_config):
        self.tools_client = ToolsClient(workflow_config, bot_config)
        
    def to_fallback(operation_type: Operation, component_type: ComponentType) -> List[Answer]:
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                # Create the specified operation
                models, sources, player = self.tools_client.create(operation_type)
                
                if component_type == ComponentType.MODEL:
                    self.executionMode = models["execution_mode"]
                    self.components = models["components"]
                    self.clients = models["clients"]
                if component_type == ComponentType.SOURCE:
                    self.executionMode = sources["execution_mode"]
                    self.components = sources["components"]
                    self.clients = sources["clients"]
                if component_type == ComponentType.PLAYER:
                    self.executionMode = player["execution_mode"]
                    self.components = player["components"]
                    self.clients = player["clients"]
                
                # Check for components availability
                if not self.components and not self.clients:
                    raise Exception("No components or clients were set! Exiting...")

                # Run the component based on execution mode
                if self.executionMode == ExecutionMode.FALLBACK:
                    return self.components[0].execute()
                
                if self.executionMode == ExecutionMode.SKIP:
                    return []

                # Proceed with the wrapped function if needed
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    def component_concatenate_results_fn(self, question, method_fn, max_results) -> List[Answer]:
        """
        Concatenates answers from multiple components by executing a question on each.

        Args:
            components (list): A list of components, that can be models, sources or players
            question: The question to be executed on each component.

        Returns:
            list: A merged list containing all answers from all components.
        """
        results = list()
        answers = []
        # max_results_per_client = math.ceil(max_results/len(self.clients)
        for client in self.clients:
            for component in self.components:
                if client.component_type == component.component_type:
                    answers = client.execute(component, question, method_fn, max_results)
            
            if not answers:
                continue
            
            results.extend(answers)
            
            if len(results) >= max_results:
                break
            
        return results

    def component_intersect_results_fn(self, question, method_fn) -> List[Answer]:
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
        filtered_results: List[Answer] = []
        answers: List[Answer] = []
        for client in self.clients:
            for component in self.components:
                if client.component_type == component.component_type:
                    answers = client.execute(component, question, method_fn)

            if not answers:
                continue
            
            if not filtered_results:
                filtered_results.extend(answers)
                continue
            
            answers_dict = {answer.text: answer for answer in answers}

            for i, filtered_result in enumerate(filtered_results):
                if filtered_result.text in answers_dict:
                    answer = answers_dict[filtered_result.text]
                    # Update if answer has a higher score
                    if filtered_result.score < answer.score:
                        filtered_results[i] = answer
                    # Remove the answer from the dict to avoid duplicates
                    del answers_dict[filtered_result.text]
                # If not found in answers_dict, do nothing (keep existing filtered_result)

            # Append remaining answers that weren't matched
            filtered_results.extend(answers_dict.values())
                    
                
        return list(filtered_results)
        
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
        