import re
import os
import sys
from innovation.FeedbackerAi.agents.llm import LLMGaming
from innovation.FeedbackerAi.agents.vlm import VLMGaming
from innovation.FeedbackerAi.agents.tools_client import Operation
from innovation.FeedbackerAi.agents.exception_handler import RetryException, QuitRequestException
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
from innovation.FeedbackerAi.agents.entities.component import Answer
from innovation.FeedbackerAi.agents.entities.component import Question
from innovation.FeedbackerAi.agents.entities.component import ComponentData
from innovation.FeedbackerAi.tools.models.entities.text import TextData, TextAnswer, TextQuestion
from innovation.FeedbackerAi.tools.sources.entities.source import SourceData, SourceAnswer, SourceQuestion
import traceback
from innovation.FeedbackerAi.tools.local.memory.cache import CacheClient
from typing import List
import itertools
import argparse
from innovation.FeedbackerAi.tools.local.logger.logger import LoggerFactory
import logging
from abc import ABC

# Init Cache
CacheClient.init_cache()
# Load Configuration
config = Utility.load_yaml()

TESTING_PATH = os.path.join(os.getcwd(), config['vlm']['testing_path'])

# Templates
GREETING_TEMPLATE = (
    "Hi! I'm an AI assistant and I'm here to help you assess your game and give you some confidence on your pitch!\n"
    "Simply send me a quick gameplay video, by telling me the filename (mp4 or avi), and I can tell you how it would fit the current audience!\n"
    "For more details on the final results, you can use the following keys:\n"
    "\tq - to quit\n"
    f"\tf=<focus> - to focus on a specific topic: {[name.lower() for name in FEATURE.__members__.keys()]}\n"
    f"\tp=<platform> - to specify which platform(s) should we use to validate your game [separated by ',']: {[name.lower() for name in PLATFORM.__members__.keys()]}\n"
    f"\ts=<source> - to specify which source(s) should we use to validate your game [separated by ',']: {[name.lower() for name in SOURCE_TYPE.__members__.keys()]}\n"
    "> start "
)

QUESTION_TEMPLATE = (
    "\nDo you want to ask anything else? As a reminder, here are some keys you can use:\n"
    "\tq - to quit\n"
    f"\tf=<focus> - to focus on a specific topic: {[name.lower() for name in FEATURE.__members__.keys()]}\n"
    f"\tp=<platform> - to specify which platform(s) should we use to validate your game [separated by ',']: {[name.lower() for name in PLATFORM.__members__.keys()]}\n"
    f"\ts=<source> - to specify which source(s) should we use to validate your game [separated by ',']: {[name.lower() for name in SOURCE_TYPE.__members__.keys()]}\n"
    "> start "
)

def hello(template, to_continue=True):
    video_filename = config["main"]['file_game']
    question = None

    while video_filename is None or question is None:
        question = input(template).strip()
        params = question.split(" ")

        if len(params) > 1 and len(params) < 4:
            video_filename = params[0]

        elif len(params) == 1:
            if params[0] == 'q':
                if to_continue:
                    raise QuitRequestException
                goodbye()
                sys.exit(0)
            else:
                video_filename = params[0] if params[0] else config["main"]['file_game']
        else:
            raise RetryException("Unexpected input data.")

        return question, video_filename


def goodbye():
    print("All good! If you need more help, you know where to find me!")
    print("Note: Keep in mind I am a simple PoC. If you find any errors or want to improve me, contact the developer Rui Gomes.")


def parse_user_input(input_str):
    focus = None
    platforms = None
    sources = None

    parts = input_str.strip().split()

    for part in parts:
        if "f=" in part:
            focus = re.split(r"f=", part, 1)[1]
        elif "p=" in part:
            platforms = re.split(r"p=", part, 1)[1].split(",")
        elif "s=" in part:
            sources = re.split(r"s=", part, 1)[1].split(",")

    
    return focus, platforms, sources

# def map_from_dict(sources_reviews: dict):
#     global genre, feature_type, source_type
#     reviews: List[Review] = []
#     for review_game in sources_reviews.values():
#         for review_game_platform_key, review_game_platform_value in review_game.items():
#             for review_game_platform_source in review_game_platform_value:
#                 for review_game_platform_source_comments_key, review_game_platform_source_comments_value in review_game_platform_source.items():
#                     for review_game_platform_source_comment in review_game_platform_source_comments_value:
#                         _source_type = SOURCE_TYPE[review_game_platform_source_comments_key]
#                         _genre = GENRE[genre.upper()]
#                         _platform = PLATFORM[review_game_platform_key]
#                         _feature_type = FEATURE[feature_type.name]
#                         review: Review = Review(review_game_platform_source_comment,
#                                                 _source_type,
#                                                 _genre,
#                                                 _platform,
#                                                 _feature_type)
#                         reviews.append(review)
#     return reviews

# def print_reviews(reviews: List[Review], exclude_vars = [], include_vars = [], verbose = True):
#     print(f"TOTAL REVIEWS: {len(reviews)}")
#     [review.print(exclude_vars = exclude_vars, include_vars=include_vars) for review in reviews]

# def filter_trends(keywords: List[str], feature_type: FEATURE_TYPE = FEATURE_TYPE.GENERAL):   
#        return feature_type.filter(keywords)


def main():   
    
    app_globals = Utility.get_globals()
    parser = argparse.ArgumentParser(
        description='FeedbackerAI CLI Tool')
    
    parser.add_argument('--verbose', default=False, action='store_true', help='sets log level to DEBUG')
    
    args = parser.parse_args()
    if args.verbose:
        LoggerFactory.logger.get(level=logging.DEBUG)

    app_globals.question, app_globals.video_filename = hello(GREETING_TEMPLATE, to_continue=False)

    workflow_config = config['main']['workflow']
    vlm_gaming = VLMGaming(workflow_config)
    llm_gaming = LLMGaming(workflow_config)

    while True:
        try:
            
            # Get input
            focus, platforms, sources = parse_user_input(app_globals.question)
            
            try: 
                app_globals.focus = FEATURE[focus] if focus else FEATURE.GENERAL
                app_globals.sources_types = [SOURCE_TYPE.ALL]
                app_globals.platforms = [PLATFORM.ALL]
                if platforms:
                    app_globals.platforms = [PLATFORM[platform] for platform in platforms]
                if sources:
                    app_globals.sources_types = [SOURCE_TYPE[source] for source in sources]
            except ValueError as ex:
                raise RetryException

            # Classify genre using VLM
            video_filename_path = os.path.join(TESTING_PATH, app_globals.video_filename)
            vlm_gaming.load_video(video_filename_path)
            
            componentData: ComponentData = ComponentData()
            
            # Get Genre
            # Questions follow the structure:
            # {
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(genre),
            #             metadata: {},
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.EXTRACT_GENRE)
            answers_genres = vlm_gaming.extract_genre()
            app_globals.genre = answers_genres[0] # Only working for 1 genre for now and as a string
            componentData.answers.extend(answers_genres)
            
            print(f"GENRE: {app_globals.genre}")
            
            # Get popular games
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(game),
            #             metadata: {}
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(game),
            #             metadata: {},
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.GET_GAMES)
            componentData.questions.extend([SourceQuestion(answer_genre.text) for answer_genre in answers_genres]) 
            answers_popular_games = llm_gaming.get_popular_games(componentData.get_last_question(), max_results=10)
            componentData.answers.extend(answers_popular_games)
            
            print(f"TOTAL GAMES: {len(answers_popular_games)}")
            Utility.log(answers_popular_games)

            # Get Reviews
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(game),
            #             metadata: {
            #                 year_max: int,
            #                 year_min: int
            #             }
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(translated review),
            #             metadata: {
            #                 platform: int,
            #                 source_type: int
            #             }
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.GET_REVIEWS)
            componentData.questions.extend([SourceQuestion(answer_popular_game.text) for answer_popular_game in answers_popular_games])    
            answers_sources_reviews = llm_gaming.get_reviews(componentData.questions, max_results_per_game=10)       
            componentData.answers.extend(answers_sources_reviews)
            
            print(f"TOTAL REVIEWS: {len(answers_sources_reviews)}")
            Utility.log(answers_sources_reviews)
            
            # Get Sentiment per Review
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(translated review),
            #             metadata: {}
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(sentiment),
            #             metadata: {
            #                 comment: str(translated review)
            #             }
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.DO_SENTIMENT_ANALYSIS)
            componentData.questions.extend([TextQuestion(answers_source_review.text) for answers_source_review in answers_sources_reviews])   
            answers_sources_sentimented_reviews = llm_gaming.get_sentiment_score(componentData.questions)
            componentData.answers.extend(answers_sources_sentimented_reviews)
            
            print(f"TOTAL SENTIMENTED REVIEWS: {len(answers_sources_sentimented_reviews)}")
            Utility.log(answers_sources_sentimented_reviews)
            
            # Get Trends per Review
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(translated review),
            #             metadata: {}
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(keywords),
            #             metadata: {}
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.GET_TRENDS)
            componentData.questions.extend([TextQuestion(answers_source_sentimented_review.metadata["comment"]) for answers_source_sentimented_review in answers_sources_sentimented_reviews])   
            answers_trends = llm_gaming.get_trends(componentData.questions, max_results_per_review=10)
            componentData.answers.extend(answers_trends)
            
            print(f"TOTAL TRENDS: {len(answers_trends)}")
            Utility.log(answers_trends)
            
            # Classify keywords
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(keywords),
            #             metadata: {}
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(feature_type),
            #             metadata: {
            #                 keyword: str(keywords)
            #             }
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.CLASSIFY_TRENDS)
            componentData.questions.extend([TextQuestion(answer_trend.text) for answer_trend in answers_trends])   
            answers_classified_trends = llm_gaming.get_classify_trends(componentData.questions, app_globals.focus)
            componentData.answers.extend(answers_classified_trends)
            
            print(f"TOTAL CLASSIFIED TRENDS: {len(answers_classified_trends)}")
            Utility.log(answers_classified_trends)        

            # Extract object features from video
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(keywords),
            #             metadata: {}
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(feature_type),
            #             metadata: {
            #                 keyword: str(keywords)
            #             }
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.EXTRACT_VIDEO_OBJECT_DETECTION_FEATURES)
            componentData.questions.extend([TextQuestion(answer_classified_trend.text) for answer_classified_trend in answers_classified_trends])   
            answers_detected_objects = vlm_gaming.get_object_features(componentData.questions, app_globals.focus)
            componentData.answers.extend(answers_detected_objects)

            print(f"TOTAL DETECTED OBJECTS: {len(answers_detected_objects)}")
            Utility.log(answers_detected_objects)
            
            # detected_objects = vlm_gaming.extract_object_features(merged_trends)
            # print(detected_objects)

            # Ask if user wants to continue or ask something else
            app_globals.question, app_globals.video_filename = hello(QUESTION_TEMPLATE)
        except RetryException as ex:
            print(f"Error found: {ex}\n Please try again...")
            traceback.print_exc()
            app_globals.question, app_globals.video_filename = hello(QUESTION_TEMPLATE)
            continue
        except QuitRequestException as ex:
            print("The user asked the application to quit...")
            break
        except Exception as ex:
            traceback.print_exc()
            break

    goodbye()


if __name__ == "__main__":
    main()
