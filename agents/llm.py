
from innovation.FeedbackerAi.tools.local.utilities import Utility
from abc import ABC, abstractmethod
from datetime import datetime
from innovation.FeedbackerAi.tools.models.model import Model, TextModel
from innovation.FeedbackerAi.tools.models.client import ModelClient
from innovation.FeedbackerAi.tools.sources.source import Source
from innovation.FeedbackerAi.tools.sources.client import SourceClient
from innovation.FeedbackerAi.tools.models.factory import ConversationFactory, QuestionAnswerFactory
from innovation.FeedbackerAi.agents.tools_client import Operation
from innovation.FeedbackerAi.agents.entities.component_type import ComponentType
from innovation.FeedbackerAi.agents.agent import Agent
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT
from typing import Optional, Dict, Any, List
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE_TYPE
from innovation.FeedbackerAi.tools.local.scripts.script_manager import ScriptManager
import copy

from innovation.FeedbackerAi.tools.local.memory.db import DB
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.tools.models.entities.text import TextQuestion
from innovation.FeedbackerAi.tools.models.entities.text import TextAnswer
from innovation.FeedbackerAi.tools.sources.entities.source import SourceQuestion
from innovation.FeedbackerAi.tools.sources.entities.source import SourceAnswer
from innovation.FeedbackerAi.tools.sources.entities.api import ApiQuestion
from innovation.FeedbackerAi.tools.sources.entities.api import ApiAnswer
from innovation.FeedbackerAi.tools.sources.entities.browser import BrowserQuestion
from innovation.FeedbackerAi.tools.sources.entities.browser import BrowserAnswer

LLM_CONFIG = Utility.load_yaml()["llm"]

class LLMGaming(Agent):
    
    def __init__(self, workflow_config):
        super().__init__(workflow_config, LLM_CONFIG)
    
    @Agent.to_fallback(Operation.GET_GAMES, ComponentType.SOURCE)
    def get_popular_games(self, question: SourceQuestion, max_results=1) -> List[SourceAnswer]:        
        current_year = datetime.now().year
    
        question.metadata = {
            "year_max": current_year,
            "year_min": current_year
        }
        
        games_answers = super().component_concatenate_results_fn(question, SourceClient.get_games, max_results)
        
        return games_answers
        
    
    @Agent.to_fallback(Operation.GET_REVIEWS, ComponentType.SOURCE)
    def get_reviews(self, questions: List[SourceQuestion], max_results_per_game=1) -> List[SourceAnswer]:
           
        games_sources_reviews = list()
        
        for question in questions:
            games_sources_reviews.extend(super().component_concatenate_results_fn(question, SourceClient.get_reviews, max_results_per_game))
            
        translated_texts = ScriptManager.translate_text([game_source_review.text for game_source_review in games_sources_reviews])
        games_sources_reviews_index = 0
        for translated_text in translated_texts: 
            games_sources_reviews[games_sources_reviews_index].text = translated_text
            DB.insert(Utility.answer_to_review(games_sources_reviews[games_sources_reviews_index]))
            games_sources_reviews_index += 1

        return games_sources_reviews
    
    def translate_comments(self, comments):   
        return [ScriptManager.translate_text(comment) for comment in comments]
    
    @Agent.to_fallback(Operation.DO_SENTIMENT_ANALYSIS, ComponentType.MODEL)
    def get_sentiment_score(self, questions: List[TextQuestion]) -> List[TextAnswer]:
                
        games_sentiments_scores = list()
        # if max_results == 0:
        #     max_results = len(questions)
        
        translated_comments = ScriptManager.translate_text([question.text for question in questions])
        for translated_comment in translated_comments:
            
            answers: List[TextAnswer] = super().component_intersect_results_fn(Question(translated_comment), ModelClient.run_model)
            
            for answer in answers:
                answer.metadata["comment"] = translated_comment
                
            games_sentiments_scores.extend(answers)
            
        for answer in answers:
            review_text = answer.metadata["comment"]
            persisted_review = DB.get_text(review_text)
            if not persisted_review:
                raise Exception(f"Review '{review_text}' not found in DB")
            persisted_review.sentiment = answer.text
                
        return games_sentiments_scores
    
    # def set_sentiment_score(self, reviews: List[Review]):
    #     self.tools_client.create(Operation.DO_SENTIMENT_ANALYSIS)
    #     models_execution_mode = self.tools_client.models["execution_mode"]
    #     models = self.tools_client.models["components"]

    #     if not models:
    #         return None
        
    #     if models_execution_mode == ExecutionMode.FALLBACK:
    #         user_input_model = models[0]
    #         model_answer = user_input_model.execute()
            
    #         idx = 0
    #         for comment in comments:
    #             sentiment = REVIEW_SENTIMENT(model_answer)
    #             reviews[idx].text = comment
    #             reviews[idx].sentiment = sentiment
    #             idx = idx+1
        
    #     comments = [review.text for review in reviews]
    #     translated_comments = ScriptManager.translate_text(comments)

    #     idx = 0
    #     for translated_comment in translated_comments:
    #         confidence_threshold_model = None
    #         for model in models:
    #             answer = model.execute(translated_comment)
                
    #             if not answer:
    #                 continue
                
    #             answer_sentiment, answer_score = answer
    #             sentiment = REVIEW_SENTIMENT.UNKNOWN
                
    #             if not confidence_threshold_model:
    #                 confidence_threshold_model = float(answer_score)
                    
    #             if float(answer_score) >= confidence_threshold_model: # In case positive and negative scores from different models are very close
    #                 try:
    #                     sentiment = REVIEW_SENTIMENT(answer_sentiment)
    #                 except Exception as ex:
    #                     print("Invalid sentiment: {answer_sentiment}")
    #                     sentiment = REVIEW_SENTIMENT.UNKNOWN
                    
    #                 # models_answers[sentiment.name].append(translated_comment)
    #                 confidence_threshold_model = float(answer_score)
    #                 reviews[idx].text = translated_comment
    #                 reviews[idx].sentiment = sentiment
    #         idx = idx+1
    
    # def get_trends(self, comments: List[str]):
        
    #     self.tools_client.create(Operation.GET_TRENDS)
    #     models_execution_mode = self.tools_client.models["execution_mode"]
    #     models = self.tools_client.models["components"]

    #     if not models:
    #         return None
        
    #     if models_execution_mode == ExecutionMode.FALLBACK:
    #         return models[0].execute()
           
    #     models_answers: List[Trend] = []
        
    #     for comment in comments:
    #         for model in models:
    #             answers = model.execute(comment)
                
    #             if not answers:
    #                 continue
                    
    #             models_answers.extend([Trend(answer) for answer in answers])
                
    #     return models_answers
    
    @Agent.to_fallback(Operation.GET_TRENDS, ComponentType.MODEL)
    def get_trends(self, questions: List[TextQuestion], max_results_per_review=1) -> List[TextAnswer]:
               
        games_trends = list()
            
        for question in questions:
            
            answers_trends = super().component_concatenate_results_fn(question, ModelClient.run_model, max_results_per_review)
            review = DB.get_text(question.text)
            for answer_trend in answers_trends:
                DB.insert_trend(review.id, Utility.answer_to_trend(answer_trend))
                
            games_trends.extend(answers_trends) 
            
        return games_trends
        
    # @Agent.to_fallback(Operation.GET_TRENDS, ComponentType.MODEL)
    # def set_trends(self, reviews: List[Review]):
        
    #     filtered_reviews = []   
    #     for review in reviews:
    #         for model in self.components:
    #             answers = model.execute(review.text)
                
    #             if not answers:
    #                 continue
                
    #             filtered_review = copy.deepcopy(review)
    #             trends = [Trend(answer) for answer in answers]
    #             filtered_review.trends.update(trends)
    #             filtered_reviews.append(filtered_review)
                
    #     reviews.clear()
    #     reviews.extend(filtered_reviews)
    
    # def classify_trends(self, reviews: List[Review], focus: FEATURE = FEATURE.GENERAL):
        
    #     self.tools_client.create(Operation.CLASSIFY_TRENDS)
    #     models_execution_mode = self.tools_client.models["execution_mode"]
    #     models = self.tools_client.models["components"]

    #     if not models:
    #         return None
        
    #     if models_execution_mode == ExecutionMode.FALLBACK:
    #         return models[0].execute()
           
    #     filtered_reviews: List[Review] = []
    #     for review in reviews:
    #         model_answers = []
    #         classified_trends: List[Trend] = []
    #         trends = review.trends
    #         for model in models:
    #             focus_subfeatures_descriptions: List[str] = focus.get_subfeatures_descriptions()
    #             answers = model.execute(([trend.name for trend in trends], focus_subfeatures_descriptions))

    #             if not answers:
    #                 continue
                
    #             if not model_answers:
    #                 model_answers.extend(answers)
    #                 continue
                    
    #             model_answers = set(Utility.get_list_tuples_with_max_value(answers, model_answers, param_match_index=0, param_max_index=2))
    #             classified_trends = set(Trend(name=model_answer[0], feature_type=focus.subfeatures[model_answer[1].upper()]) for model_answer in model_answers)
            
    #         if classified_trends:
    #             filtered_review = copy.deepcopy(review)
    #             filtered_review.trends.clear()
    #             filtered_review.trends = classified_trends
    #             filtered_reviews.append(filtered_review)
                      
    #     reviews.clear()
    #     reviews.extend(filtered_reviews)
    
    @Agent.to_fallback(Operation.CLASSIFY_TRENDS, ComponentType.MODEL)
    def get_classify_trends(self, questions: List[TextQuestion], focus: FEATURE = FEATURE.GENERAL) -> List[TextAnswer]:
           
        filtered_questions_text = {question.text for question in questions}
        focus_subfeatures_descriptions: List[str] = focus.get_subfeatures_descriptions()
        
        classified_games_trends = list()
        for filtered_question_text in filtered_questions_text:
    
            answers: List[TextAnswer] = super().component_intersect_results_fn(
                Question(
                    filtered_question_text, 
                    metadata={"labels": focus_subfeatures_descriptions}),
                ModelClient.run_model)
                
            classified_games_trends.extend(answers)
                
        return classified_games_trends
        
    # @Agent.to_fallback(Operation.CLASSIFY_TRENDS, ComponentType.MODEL)
    # def classify_trends(self, reviews: List[Review], focus: FEATURE = FEATURE.GENERAL):
           
    #     filtered_reviews: List[Review] = []
    #     focus_subfeatures_descriptions: List[str] = focus.get_subfeatures_descriptions()
    #     for review in reviews:
            
    #         model_answers = []
    #         classified_trends: List[Trend] = []
    #         trends = review.trends

    #         model_answers = super().component_intersect_results_fn(question=([trend.name for trend in trends], focus_subfeatures_descriptions), 
    #                                              param_match_index=0, param_max_index=2)
                     
    #         for model_answer in model_answers:
    #             classified_trends = set(Trend(name=model_answer[0], feature_type=focus.subfeatures[model_answer[1].upper()]))
            
    #         if classified_trends:
    #             filtered_review = copy.deepcopy(review)
    #             filtered_review.trends.clear()
    #             filtered_review.trends = classified_trends
    #             filtered_reviews.append(filtered_review)
                      
    #     reviews.clear()
    #     reviews.extend(filtered_reviews)
            # for classfied_trend in classfied_trends:
            #     if classfied_trend["name"] in Utility.get_list_by_column(answers, 0) and classfied_trend["score"] in Utility.get_list_by_column(answers, 2):
            #         classfied_trends = Utility.intersect_lists_by_strings(classfied_trends, Utility.get_list_by_column(answers, 0))    
        
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
    
    # def classify_trends(self, genre):
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
   

