from innovation.FeedbackerAi.agents.exception_handler import QuitRequestException
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.tools.fallback.user_input import UserInput
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import List
from enum import Enum


class ConsoleInput(UserInput):
    
    def __init__(self, bot_operation: Enum):
        
        super().__init__(bot_operation.description, bot_operation.is_multiple_answers_allowed)
        self.available_options = bot_operation.output_available_options


    def execute(self):
        
        # In case of Non-Json
        if self.available_options: 
            available_options = [name.lower() for name in self.available_options.__members__.keys()]
            answer = self.build_question_template(available_options)
            
            if not hasattr(self.available_options, answer.upper()):
                print(f"Option \'{answer}\' not found! Try again...")
                return self.execute()
        
            if self.is_multiple_answers_allowed:
                answers = answer.split(" ")
                return [Answer(answer) for answer in answers]
            return [Answer(answer)]