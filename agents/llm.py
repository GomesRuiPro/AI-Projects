
from tools.utilities import Utility
from abc import ABC, abstractmethod
from datetime import datetime
from tools.models.model import Model, TextModel
from tools.sources.external.metacritic import MetacriticClient
from tools.models.factory import ConversationFactory, QuestionAnswerFactory
from agents.agent import Agent


APIS_CONFIG = Utility.load_yaml()["apis"]
TOOLS_CONFIG = Utility.load_yaml()["local"]
LLM_CONFIG = Utility.load_yaml()["llm"]

class LLMGaming(Agent):
    
    def __init__(self):
        super().__init__()
    
    def start_model(self, *with_features):
        self.models = {
            "conversation": None,
            "question_answer": None,
            "translation": None
        }
        self.source_clients = {
            "games": None,
            "trends": None,
            "feedback": [None]
        }
        
        for with_feature in with_features:
            if "model" in with_feature:
                if with_feature == "with_conversation":
                    self.models["conversation"] = Conversation.create()
                elif with_feature == "with_question_answer":
                    self.models["question_answer"] = QuestionAnswer.create()
                elif with_feature == "with_translation":
                    self.models["translation"] = None
            elif "source" in with_feature:
                if with_feature == "with_source_games":
                    self.source_clients["games"] = GamesSource.create()

    def get_source_client(self, source_type):
        return self.source_clients[source_type]

    def get_source_clients(self):
        return self.source_clients
    
    # def get_trends(self, genre):
    #     context = f"I am trying to understand the player behavior and how it is moving torwards the future of {genre} videogames. I would like to know what players comment in social mediawould like to see more and less for future videogames."
    #     question = f"What are the currently most hated features and the most desired features in this {genre}?"
    #     model = self.get_model("question_answer")
    #     return model.execute((question,context))
    
    # def get_trends(self, genre):
    #     question = f"What gameplay features should a {genre} video game have? Give me a list of the most 10 popular features splitted by commas."
    #     model = self.get_model("conversation")
    #     return model.execute(question)
    
    # def get_trends(self, genre):
    #     query = f"Best {genre} games of this month"
        
        
    #     Utility.get_video_comments("")
    
    def get_popular_games(self, genre, max_results=10):
        client: MetacriticClient = self.get_source_client("games")
        current_year = datetime.now().year
        return client.get_games(genre, current_year, current_year, max_results)
            
        
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
    
class SourceClient(ABC):
    
    source = None

    @abstractmethod
    def create():
        pass
    
class GamesSource(SourceClient):

    # Making the method simple to not focus on fallback or any factory. it moves directly to the intended source,
    # but this should be updated in the future to dynamically should one or multiple source_clients
    @staticmethod
    def create():
        config = TOOLS_CONFIG['sources']['games']
        SourceClient.source  = MetacriticClient(config)
        return SourceClient.source    


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
