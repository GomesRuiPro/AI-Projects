import os
from innovation.FeedbackerAi.tools.local.utilities import Utility
from abc import ABC
import datetime
from typing import Optional, Dict, Any, Set, List
from innovation.FeedbackerAi.tools.local.entities.review import Review, Trend

class DB(ABC):
    
    reviews: Set[Review] = set()
    
    @staticmethod
    def insert(review: Review):
        DB.reviews.add(review)
        
    @staticmethod
    def insert_trend(id: int, trend: Trend):
        review = DB.__get(id)
        review.trends.append(trend)
        trend.review = review
        
    @staticmethod
    def update(id: int, review: Review):
        DB.__get(id)
        DB.delete(id)
        DB.insert(review)
        
    @staticmethod
    def update_trend(review_id: int, id: int, trend: Trend):
        DB.__get(review_id)
        DB.__get_trend(id)
        DB.delete_trend(id)
        DB.insert_trend(trend)
        
    @staticmethod
    def delete(id: int):
        review = DB.__get(id)
        if review:
            del review
            
    @staticmethod
    def delete_trend(review_id: int, id: int):
        review = DB.__get(review_id)
        if review:
            trend = DB.__get_trend(id)
            if trend:
                del trend
            
    @staticmethod
    def __get(id: int):
        review = DB.get(id)
        if not review:
            raise Exception(f"Review {id} not found!")
        return review
    
    @staticmethod
    def __get_trend(review_id: int, id: int):
        trend = DB.get_trend(review_id)
        if not trend:
            raise Exception(f"Trend {id} not found in Review {review_id}!")
        return trend
    
    @staticmethod
    def get(id: int):
        for review in DB.reviews:
            if review.id == id:
                return review
        return None
    
    @staticmethod
    def get_trend(review_id: int, id: int):
        for review in DB.reviews:
            if review.id == review_id:
                for trend in review.trends:
                    if trend.id == id:
                        return trend
        return None
    
    @staticmethod
    def get_text(text: str):
        for review in DB.reviews:
            if review.text == text:
                return review
        return None
    
    @staticmethod
    def get_all():
        return DB.reviews