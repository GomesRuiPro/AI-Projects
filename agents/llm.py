
from tools.utilities import Utility
from abc import ABC, abstractmethod
from tools.models.model import Model, TextModel
from tools.models.factory import ConversationFactory, QuestionAnswerFactory


APIS_CONFIG = Utility.load_yaml()["apis"]
LLM_CONFIG = Utility.load_yaml()["llm"]

class LLMGaming:
    models = []
    
    def __init__(self):
        pass
    
    def start_model(self, with_conversation=False, with_question_answer=False):
        conversation_model = Conversation.create() if with_conversation else None
        question_answer_model = QuestionAnswer.create() if with_question_answer else None
        self.models = {'conversation': conversation_model, 'question_answer': question_answer_model}
        
    def get_model(self, model_type):
        return self.models[model_type]

    def get_models(self):
        return self.models

    # def get_trends(self, genre):
    #     context = f"I am trying to understand the player behavior and how it is moving torwards the future of {genre} videogames. I would like to know what players comment in social mediawould like to see more and less for future videogames."
    #     question = f"What are the currently most hated features and the most desired features in this {genre}?"
    #     model = self.get_model("question_answer")
    #     return model.execute((question,context))
    
    # def get_trends(self, genre):
    #     question = f"What gameplay features should a {genre} video game have? Give me a list of the most 10 popular features splitted by commas."
    #     model = self.get_model("conversation")
    #     return model.execute(question)
    
    def get_popular_games(self, genre):
        Utility.web_scrapping()
    def get_trends(self, genre):
        query = f"Best {genre} games of this month"
        
        
        Utility.get_video_comments("")
class ModelClient(ABC):

    model = None

    @abstractmethod
    def create():
        pass


class Conversation(ModelClient):

    @staticmethod
    def create():
        config = LLM_CONFIG['models']['conversation']
        conversationFactory = ConversationFactory(
            config, APIS_CONFIG['hugging_face']['token'])
        ModelClient.model = conversationFactory.create(
            LLM_CONFIG['use_model_finetuned'], LLM_CONFIG['device_debug'])
        return ModelClient.model

class QuestionAnswer(ModelClient):

    @staticmethod
    def create():
        config = LLM_CONFIG['models']['question_answer']
        questionAnswerFactory = QuestionAnswerFactory(
            config, APIS_CONFIG['hugging_face']['token'])
        ModelClient.model = questionAnswerFactory.create(
            LLM_CONFIG['use_model_finetuned'], LLM_CONFIG['device_debug'])
        return ModelClient.model    


    # def generate_search_queries(self, query, number_of_results=1):
    #     question_llm_template = (
    #         "Hi! Generate a list of {number_of_results} search queries for videos about {query}  splitted by ','. Don't send me any extra details or comments."
    #         "Thank you!"
    #     )

    #     prompt = ChatPromptTemplate.from_template(question_llm_template)
    #     chain = prompt | self.__model
    #     result = chain.invoke({"number_of_results": number_of_results, "query": query})

    #     queries = result.split(',')[:number_of_results]
    #     if not queries or len(queries) != number_of_results:
    #         raise Exception(f"LLM provided unexpected response: {result}")
    #     return queries
    
    # def get_list_games(self, genre, number_of_results):
    #     question_llm_template = (
    #         "Hi! Give me a list of size {number_of_results} with the most popular and recent {genre} games this year splitted by ','. Don't send me any extra details or comments."
    #         "Thank you!"
    #     )

    #     prompt = ChatPromptTemplate.from_template(question_llm_template)
    #     chain = prompt | self.__model
    #     result = chain.invoke({"number_of_results": number_of_results, "genre": genre})
        
    #     queries = result.split(',')[:number_of_results]
    #     quoted_words = [f"\"{word}\"" for word in queries]
    #     if not quoted_words or len(quoted_words) != number_of_results:
    #         raise Exception(f"LLM provided unexpected response: {result}")
    #     return quoted_words

    # def get_detailed_trends(self, focus, genre, sources):
    #     question_llm_template = (
    #         "Hi! I need to figure out what gaming players are looking for in the future. "
    #         "Can you give me a list of the most desired and the most hated {focus} features the {genre} videogames should have? "
    #         "The answer should be a simple list sorted from the most mentioned to the least with keywords and without descriptions. "
    #         "Also insert the total number of mentions per feature and its percentage. "
    #         "Your sources should be {sources}. "
    #         "Thank you!"
    #     )

    #     prompt = ChatPromptTemplate.from_template(question_llm_template)
    #     chain = prompt | self.__model
    #     result = chain.invoke({"focus": focus, "genre": genre, "sources": sources})

    #     return result
    
    # def get_trends(self, genre):
    #     result = {}
    #     question_llm_template = (
    #         "Hi! I need to figure out what gaming players are looking for in the future. "
    #         "Provide me a list of the 10 most {topic} gameplay features in today's videogames specific to the {genre} genre as keywords with each feature separated by \",\". "
    #         "Use this as an example: list: \"feature1\", \"feature2\", \"feature3\"..."
    #         "Skip any extra details. "
    #         "Thank you!"
    #     )

    #     prompt = ChatPromptTemplate.from_template(question_llm_template)
    #     chain = prompt | self.__model
    #     answer = chain.invoke({"topic": "hated", "genre": genre})
    #     result["hated"] = Utility.substring_from_char(answer, ':').split(',')
    #     answer = chain.invoke({"topic": "desired", "genre": genre})
    #     result["desired"] = Utility.substring_from_char(answer, ':').split(',')
        
    #     return result
