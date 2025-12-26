from innovation.FeedbackerAi.agents.exception_handler import QuitRequestException
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.tools.local.entities.component import Component
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import List
from enum import Enum
from abc import abstractmethod, ABC

class UserInput(Component, ABC):
    is_multiple_answers_allowed = False
    available_options: Enum = None

    # def __init__(self, component_name, topic, is_multiple_answers_allowed=False):
    #     super().__init__(None, component_name)
            
    #     self.question_template = """This component is under construction and cannot be used. However, we can mock its result :)
    #         What would you expect the component \"{component_name}\" response to be about the {topic}?
    #     q - to quit """
        
    #     self.topic = topic
    #     self.is_multiple_answers_allowed = is_multiple_answers_allowed
        
    def __init__(self, topic, is_multiple_answers_allowed=False):
        
        super().__init__(None, None)
            
        self.question_template = """This component is under construction and cannot be used. However, we can mock its result :)
            What would you expect the result from the operation {topic}?
            {available_options_str}
            q - to quit """
        self.topic = topic
        self.is_multiple_answers_allowed = is_multiple_answers_allowed

    @abstractmethod
    def execute(self):
        pass
        
        
    
    def build_question_template(self, available_options):
        available_options_str = f"Available options: {available_options}"
        questionTemplate = self.question_template.format(
            component_name=self.name, topic=self.topic, available_options_str=available_options_str)
        if self.is_multiple_answers_allowed:
            questionTemplate += "\nMultiple answers are possible, as long it is splitted by a \"space\""
        else:
            questionTemplate += "\nOnly one answer is possible"

        questionTemplate += "\n> "
        answer = input(questionTemplate).strip()

        if answer == 'q':
            raise QuitRequestException
        
        return answer