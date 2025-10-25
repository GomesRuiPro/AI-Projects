
from innovation.FeedbackerAi.tools.local.utilities import Utility
from abc import ABC, abstractmethod
from datetime import datetime
from innovation.FeedbackerAi.tools.models.model import Model, TextModel
from innovation.FeedbackerAi.tools.sources.external.browser.metacritic import MetacriticClient
from innovation.FeedbackerAi.tools.models.factory import ConversationFactory, QuestionAnswerFactory
from innovation.FeedbackerAi.agents.tools_client import Operation, ToolsFactory, ExecutionMode
from innovation.FeedbackerAi.agents.agent import Agent
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT
from typing import Optional, Dict, Any, List

LLM_CONFIG = Utility.load_yaml()["llm"]

class LLMGaming(Agent):
    
    def __init__(self, workflow_config):
        super().__init__(workflow_config, LLM_CONFIG)
    
    # def start_model(self, *with_features):
        # self.models = {
        #     "conversation": None,
        #     "question_answer": None,
        #     "translation": None
        # }
        # self.source_clients = {
        #     "games": None,
        #     "trends": None,
        #     "feedback": [None]
        # }
        
        # for with_feature in with_features:
        #     if "model" in with_feature:
        #         if with_feature == "with_conversation":
        #             self.models["conversation"] = Conversation.create()
        #         elif with_feature == "with_question_answer":
        #             self.models["question_answer"] = QuestionAnswer.create()
        #         elif with_feature == "with_translation":
        #             self.models["translation"] = None
        #     elif "source" in with_feature:
        #         if with_feature == "with_source_games":
        #             self.source_clients["games"] = GamesSource.create()

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
    
    def get_popular_games(self, genre: str, max_results=10):
        self.tools_client.create(Operation.GET_GAMES)
        sources_execution_mode = self.tools_client.sources["execution_mode"]
        sources = self.tools_client.sources["entities"]

        if not sources:
            return None
        
        if sources_execution_mode == ExecutionMode.FALLBACK:
            return sources[0].execute()
        
        current_year = datetime.now().year
    
        games = []
        for source in sources:
            games.extend(source.get_games(genre, current_year, current_year, max_results))
        return games
    
    def get_reviews(self, games: List[str], max_results=10):
        self.tools_client.create(Operation.GET_REVIEWS)
        sources_execution_mode = self.tools_client.sources["execution_mode"]
        sources = self.tools_client.sources["entities"]

        if not sources:
            return None
        
        if sources_execution_mode == ExecutionMode.FALLBACK:
            return sources[0].execute()
           
        games_sources_reviews = {}
        for game in games:
            sources_reviews = []
            
            for source in sources:
                reviews_source = source.get_reviews(game, max_results)
                sources_reviews.append(reviews_source)
                
            sources_reviews_merged = Utility.merge_list_of_dicts(sources_reviews)
            games_sources_reviews[game] = sources_reviews_merged
        return games_sources_reviews
    
    def get_sentiment_score(self, comments: List[str]):
        self.tools_client.create(Operation.DO_SENTIMENT_ANALYSIS)
        models_execution_mode = self.tools_client.models["execution_mode"]
        models = self.tools_client.models["entities"]

        if not models:
            return None
        
        if models_execution_mode == ExecutionMode.FALLBACK:
            return models[0].execute()
           
        # REVIEW_SENTIMENT.UNKNOWN.name: text
        
        models_answers = {
            "NEGATIVE": [],
            "POSITIVE": [],
            "NEUTRAL": []
        }
        
        for comment in comments:
            confidence_threshold_model = None
            for model in models:
                answer = model.execute(comment)
                
                if not answer:
                    continue
                
                answer_sentiment, answer_score = answer
                sentiment = REVIEW_SENTIMENT.UNKNOWN
                
                if not confidence_threshold_model:
                    confidence_threshold_model = float(answer_score)
                    
                if float(answer_score) >= confidence_threshold_model: # In case positive and negative scores from different models are very close
                    try:
                        sentiment = REVIEW_SENTIMENT(answer_sentiment)
                    except Exception as ex:
                        print("Invalid sentiment: {answer_sentiment}")
                        sentiment = REVIEW_SENTIMENT.UNKNOWN
                    
                    models_answers[sentiment.name].append(comment)
                    confidence_threshold_model = float(answer_score)
                
        return models_answers
    
    def get_trends(self, comments: List[str]):
        
        self.tools_client.create(Operation.GET_KEYWORDS)
        models_execution_mode = self.tools_client.models["execution_mode"]
        models = self.tools_client.models["entities"]

        if not models:
            return None
        
        if models_execution_mode == ExecutionMode.FALLBACK:
            return models[0].execute()
           
        models_answers: List[str] = []
        
        for comment in comments:
            for model in models:
                answers = model.execute(comment)
                
                if not answers:
                    continue
                    
                models_answers.extend(answers)
                
        return models_answers
            
        
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
   

