from core.exception_handler import QuitRequestException
from tools.models.model import Model


class UserInput(Model):
    topic = ""
    model_name = ""
    is_multiple_answers_allowed = False

    QUESTION_TEMPLATE = """This model is under construction and cannot be used. However, we can mock its result :)
    What would you expect the model \"{model_name}\" response to be about the {topic}?
        q - to quit """

    def __init__(self, model_name, topic, is_multiple_answers_allowed=False):
        super().__init__(None, model_name)
        self.topic = topic
        self.is_multiple_answers_allowed = is_multiple_answers_allowed

    def execute(self):
        questionTemplate = UserInput.QUESTION_TEMPLATE.format(
            model_name=self.model_name, topic=self.topic)
        if self.is_multiple_answers_allowed:
            questionTemplate += "\nMultiple answers are possible, as long it is splitted by a \"space\""
        else:
            questionTemplate += "\nOnly one answer is possible"

        questionTemplate += "\n> "
        answer = input(questionTemplate).strip()

        if answer == 'q':
            raise QuitRequestException
        if self.is_multiple_answers_allowed:
            answers = answer.split(" ")
            return answers
        return answer
