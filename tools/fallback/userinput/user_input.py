from innovation.FeedbackerAi.agents.exception_handler import QuitRequestException
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.tools.local.entities.component import Component
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import List
from enum import Enum


class UserInput(Component):
    is_multiple_answers_allowed = False
    available_options: Enum = None

    def __init__(self, component_name, topic, is_multiple_answers_allowed=False):
        super().__init__(None, component_name)
            
        self.question_template = """This component is under construction and cannot be used. However, we can mock its result :)
            What would you expect the component \"{component_name}\" response to be about the {topic}?
        q - to quit """
        
        self.topic = topic
        self.is_multiple_answers_allowed = is_multiple_answers_allowed
        
    def __init__(self, bot_operation: Enum, is_multiple_answers_allowed=False):
        
        super().__init__(None, None)
            
        self.question_template = """This component is under construction and cannot be used. However, we can mock its result :)
            What would you expect the result from the operation {topic}?
            {available_options_str}
            q - to quit """
        self.topic = bot_operation.description
        self.available_options = bot_operation.output_available_options
        self.is_multiple_answers_allowed = is_multiple_answers_allowed

    def execute(self) -> List[Answer]:
        
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
        else:
            
            available_options = Utility.get_list_files(f"data/testing/input/{self.topic}", is_dir=True)
            answer_filepath = self.build_question_template(available_options)
            
            if answer_filepath.isdigit():
                answer_filepath = available_options[int(answer_filepath)][0]
            
            try:
                componentData = Utility.read_json_from_file(answer_filepath)
                return [Answer(answer_json["text"], answer_json["metadata"]) for answer_json in componentData["answers"]]
            except Exception as e:
                print(f"Bad json format: {e.__cause__}! Try again...")
                return self.execute()
        
    
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