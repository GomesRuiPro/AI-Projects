from innovation.FeedbackerAi.agents.exception_handler import QuitRequestException
from innovation.FeedbackerAi.tools.models.model import Model
from typing import Optional, Dict, Any, List
from enum import Enum


class UserInput(Model):
    is_multiple_answers_allowed = False
    available_options: Enum = None

    def __init__(self, model_name, topic, is_multiple_answers_allowed=False):
        super().__init__(None, model_name)
            
        self.question_template = """This model is under construction and cannot be used. However, we can mock its result :)
            What would you expect the model \"{model_name}\" response to be about the {topic}?
            {available_options_str}
        q - to quit """
        
        self.topic = topic
        self.is_multiple_answers_allowed = is_multiple_answers_allowed
        
    def __init__(self, topic, is_multiple_answers_allowed=False):
        super().__init__(None, None)
            
        self.question_template = """This model is under construction and cannot be used. However, we can mock its result :)
            What would you expect the result from the operation {topic}?
            {available_options_str}
            q - to quit """
        self.topic = topic
        self.is_multiple_answers_allowed = is_multiple_answers_allowed

    def execute(self):
        available_options = [name.lower() for name in self.available_options.__members__.keys()] if self.available_options else "Unavailable"
        available_options_str = f"Available options: {available_options}"
        questionTemplate = self.question_template.format(
            model_name=self.model_name, topic=self.topic, available_options_str=available_options_str)
        if self.is_multiple_answers_allowed:
            questionTemplate += "\nMultiple answers are possible, as long it is splitted by a \"space\""
        else:
            questionTemplate += "\nOnly one answer is possible"

        questionTemplate += "\n> "
        answer = input(questionTemplate).strip()

        if answer == 'q':
            raise QuitRequestException
        
        if not hasattr(self.available_options, answer.upper()):
            print(f"Option \'{answer}\' not found! Try again...")
            return self.execute()
        
        if self.is_multiple_answers_allowed:
            answers = answer.split(" ")
            return answers
        return answer
