
from abc import ABC
import datetime
from typing import Optional, Dict, Any, Set, List
from innovation.FeedbackerAi.tools.local.entities.review import Review, Trend
import uuid

class DB(ABC):
    
    reviews: List[Review] = list()
    trends: List[Trend] = list()
    
    @staticmethod
    def insert(review: Review):
        DB.reviews.append(review)
        return review
        
    @staticmethod
    def insert_trend(id: uuid, trend: Trend):
        DB.trends.append(trend)
        review = DB.__get(id)
        review.trends.append(trend)
        trend.review = review
        return trend
        
    @staticmethod
    def delete(id: uuid):
        review = DB.__get(id)
        if review:
            del review
            
    @staticmethod
    def delete_trend(review_id: uuid, id: uuid):
        review = DB.__get(review_id)
        if review:
            trend = DB.__get_trend(id)
            if trend:
                del trend
            
    @staticmethod
    def __get(id: uuid):
        review = DB.get(id)
        if not review:
            raise Exception(f"Review {id} not found!")
        return review
    
    @staticmethod
    def __get_trend(review_id: uuid, id: uuid):
        trend = DB.get_trend(review_id)
        if not trend:
            raise Exception(f"Trend {id} not found in Review {review_id}!")
        return trend
    
    @staticmethod
    def get(id: uuid):
        for review in DB.reviews:
            if review.id == id:
                return review
        return None
    
    @staticmethod
    def get_trend(id: uuid):
        for trend in DB.trends:
            if trend.id == id:
                return trend
        return None
    # @staticmethod
    # def get_trend(review_id: uuid, id: uuid):
    #     for review in DB.reviews:
    #         if review.id == review_id:
    #             for trend in review.trends:
    #                 if trend.id == id:
    #                     return trend
    #     return None
    
    @staticmethod
    def get_trend_by_name(name: str):
        for trend in DB.trends:
            if trend.name == name:
                return trend
        return None
    
    @staticmethod
    def get_review_by_text(text: str):
        for review in DB.reviews:
            if review.text == text:
                return review
        return None
    
    @staticmethod
    def get_review_by_trend_name(name: str):
        for review in DB.reviews:
            trend = DB.get_trend_by_name(name)
            if trend:
                return review
        return None
    
    @staticmethod
    def get_all_reviews():
        return DB.reviews
    
    @staticmethod
    def get_all_trends():
        return DB.trends