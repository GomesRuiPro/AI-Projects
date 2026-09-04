from innovation.FeedbackerAi.agents.exception_handler import QuitRequestException
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.tools.fallback.user_input import UserInput
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import List
from enum import Enum


class JsonInput(UserInput):
    
    def __init__(self, bot_operation: Enum):
        super().__init__(bot_operation.description, bot_operation.is_multiple_answers_allowed)
        self.available_options = Utility.get_list_files(f"data/testing/input/{self.topic}", is_dir=True)

    def execute(self):
        
        answer_filepath = self.build_question_template(self.available_options)
        
        if answer_filepath.isdigit():
            answer_filepath = self.available_options[int(answer_filepath)][0]
        
        try:
            componentData = Utility.read_json_from_file(answer_filepath)
            return [Answer(answer_json["text"], answer_json["metadata"]) for answer_json in componentData["answers"]]
        except Exception as e:
            print(f"Bad json format: {e.__cause__}! Try again...")
            return self.execute()