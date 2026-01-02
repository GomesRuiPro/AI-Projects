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
from innovation.FeedbackerAi.tools.local.memory.db import DB
from innovation.FeedbackerAi.tools.local.entities.review_sentiment import REVIEW_SENTIMENT
from innovation.FeedbackerAi.tools.local.scripts.script_manager import ScriptManager
from innovation.FeedbackerAi.tools.local.entities.review import Review, Trend
from datetime import date, datetime
from collections import Counter

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

def create_report_data(provided_reviews, demanded_reviews):
    # Helper function to filter reviews by sentiment
    def filter_reviews_by_sentiment(reviews, sentiment):
        return [review for review in reviews if review.sentiment == sentiment]

    # Helper function to extract all trends from a list of reviews
    def extract_trends(reviews):
        trends = []
        for review in reviews:
            trends.extend(review.trends)
        return trends
    
    # Calculate most and least features
    def get_feature_extremes(trends: List[Trend], func) -> List:
        results = None
        if trends:
            feature_values = Counter([trend.feature_type for trend in trends])
            # Find the maximum count
            extreme = func(feature_values.values())

            # Retrieve all keys with that max count
            results = ",".join([key.name for key, count in feature_values.items() if count == extreme])
        
        return results if results else FEATURE.UNKNOWN.name

    # Filter reviews by sentiment
    negative_provided = filter_reviews_by_sentiment(provided_reviews, REVIEW_SENTIMENT.NEGATIVE)
    negative_demanded = filter_reviews_by_sentiment(demanded_reviews, REVIEW_SENTIMENT.NEGATIVE)
    positive_provided = filter_reviews_by_sentiment(provided_reviews, REVIEW_SENTIMENT.POSITIVE)
    positive_demanded = filter_reviews_by_sentiment(demanded_reviews, REVIEW_SENTIMENT.POSITIVE)

    # Extract trends
    negative_provided_trends: List[Trend] = extract_trends(negative_provided)
    negative_demanded_trends: List[Trend] = extract_trends(negative_demanded)
    positive_provided_trends: List[Trend] = extract_trends(positive_provided)
    positive_demanded_trends: List[Trend] = extract_trends(positive_demanded)
    all_demanded_trends: List[Trend] = extract_trends(demanded_reviews)
    all_provided_trends: List[Trend] = extract_trends(provided_reviews)

    most_demanded_feature = get_feature_extremes(all_demanded_trends, max)
    least_demanded_feature = get_feature_extremes(all_demanded_trends, min)
    most_provided_feature = get_feature_extremes(all_provided_trends, max)
    least_provided_feature = get_feature_extremes(all_provided_trends, min)

    most_hated_feature = FEATURE.UNKNOWN.name
    least_hated_feature = FEATURE.UNKNOWN.name
    if negative_demanded_trends:
        most_hated_feature = get_feature_extremes(negative_demanded_trends, max)
        least_hated_feature = get_feature_extremes(negative_demanded_trends, min)
        
    most_damaging_feature = FEATURE.UNKNOWN.name
    least_damaging_feature = FEATURE.UNKNOWN.name
    if negative_provided_trends:
        most_damaging_feature = get_feature_extremes(negative_provided_trends, max)
        least_damaging_feature = get_feature_extremes(negative_provided_trends, min)

    # Find common trends
    to_have_trends: List[Trend] = list(set(positive_demanded).intersection(set(positive_provided))) if positive_demanded else []
    not_to_have_trends: List[Trend] = list(set(negative_provided).intersection(set(negative_demanded))) if negative_provided else []

    # Calculate final score
    final_score = None
    if to_have_trends or not_to_have_trends:
        final_score = Utility.calculate_score(to_have_trends, not_to_have_trends, config["report"]["formula"])

    # Prepare report
    title = f"{Utility.GLOBALS.focus.name} Report - {date.today()}"

    return {
        "title": title,
        "data": [
            {"table": "Demanded features", "data": [positive_demanded_trend.to_dict() for positive_demanded_trend in positive_demanded_trends]},
            {"table": "Hated features", "data": [negative_demanded_trend.to_dict() for negative_demanded_trend in negative_demanded_trends]},
            {"table": "Features detected in the game", "data": [all_provided_trend.to_dict() for all_provided_trend in all_provided_trends]},
            {"table": "Lacking features in the game", "data": [to_have_trend.to_dict() for to_have_trend in to_have_trends]},
            {"table": "Non-required features in the game", "data": [not_to_have_trend.to_dict() for not_to_have_trend in not_to_have_trends]},
            {"graph": "Images", "data": []},
            {"section": "Summary", "data": [
                {"text": "Genre detected", "data": str(Utility.GLOBALS.genre).capitalize()},
                {"text": "Final score", "data": str(final_score) if final_score else "Not defined"}]},
            {"section": "Details", "data": [
                {"text": "most_demanded_feature", "data": most_demanded_feature},
                {"text": "least_demanded_feature", "data": least_demanded_feature},
                {"text": "most_provided_feature", "data": most_provided_feature},
                {"text": "least_provided_feature", "data": least_provided_feature},
                {"text": "most_hated_feature", "data": most_hated_feature},
                {"text": "least_hated_feature", "data": least_hated_feature},
                {"text": "most_damaging_feature", "data": most_damaging_feature},
                {"text": "least_damaging_feature", "data": least_damaging_feature}
            ]},
            {"section": "Footer", "data": [{"text": "", "data": "Generated by Feedbacker AI"}]}
        ]
    }

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
            answers = vlm_gaming.extract_genre()
            app_globals.genre = answers[0].text if answers else GENRE.UNKNOWN.name # Only working for 1 genre for now and as a string
            componentData.answers.extend(answers)
            
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
            questions = [SourceQuestion(app_globals.genre)]
            componentData.questions.extend(questions) 
            answers = llm_gaming.get_popular_games(componentData.get_last_question(), max_results=10)
            componentData.answers.extend(answers)
            
            print(f"TOTAL GAMES: {len(answers)}")
            Utility.log(answers)

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
            questions = [SourceQuestion(answer_popular_game.text) for answer_popular_game in answers]
            componentData.questions.extend(questions)    
            answers = llm_gaming.get_reviews(componentData.questions, max_results_per_game=10)       
            componentData.answers.extend(answers)
                
            # Note: we need to perform a list of strings due to performance of the script
            if answers:
                translated_texts = ScriptManager.translate_text([game_source_review.text for game_source_review in answers])
                games_sources_reviews_index = 0
                for translated_text in translated_texts: 
                    answers[games_sources_reviews_index].text = translated_text
                    DB.insert(Utility.answer_to_review(answers[games_sources_reviews_index]))
                    games_sources_reviews_index += 1
            
            print(f"TOTAL REVIEWS: {len(answers)}")
            Utility.log(answers)
            
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
            questions = [TextQuestion(answers_source_review.text) for answers_source_review in answers]
            componentData.questions.extend(questions)   
            answers = llm_gaming.get_sentiment_score(componentData.questions)
            componentData.answers.extend(answers)
        
            for answer in answers:
                review_text = answer.metadata["comment"]
                persisted_review = DB.get_review_by_text(review_text)
                if not persisted_review:
                    DB.insert(Utility.answer_to_review(answer))
                persisted_review.sentiment = REVIEW_SENTIMENT[answer.text.upper()]
            
            print(f"TOTAL SENTIMENTED REVIEWS: {len(answers)}")
            Utility.log(answers)
            
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
            #             text: str(keyword),
            #             metadata: {
            #               comment: str
            #             }
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.GET_TRENDS)
            questions = [TextQuestion(answers_source_sentimented_review.metadata["comment"]) for answers_source_sentimented_review in answers]
            componentData.questions.extend(questions)   
            answers = llm_gaming.get_trends(componentData.questions, max_results_per_review=10)
            componentData.answers.extend(answers)
            
            for answer in answers:
                review = DB.get_review_by_text(answer.metadata["comment"])
                DB.insert_trend(review.id, Utility.answer_to_trend(answer))
            
            print(f"TOTAL TRENDS: {len(answers)}")
            Utility.log(answers)
            
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
            questions = [TextQuestion(answer_trend.text) for answer_trend in answers]
            componentData.questions.extend(questions)   
            answers = llm_gaming.get_classify_trends(componentData.questions, app_globals.focus)
            componentData.answers.extend(answers)
            
            for answer in answers:
                trend_name = answer.metadata["keyword"]
                persisted_trend = DB.get_trend_by_name(trend_name)
                if not persisted_trend:
                    review = DB.get_review_by_trend_name(trend_name)
                    if not review:
                        review = DB.insert(Review("unknown", Utility.GLOBALS.genre, PLATFORM.UNKNOWN, SOURCE_TYPE.UNKNOWN, Utility.GLOBALS.focus))
                        review.sentiment = REVIEW_SENTIMENT.NEUTRAL
                    persisted_trend = DB.insert_trend(review.id, Trend(trend_name))
                persisted_trend.feature_type = FEATURE[answer.text.upper()]
            
            print(f"TOTAL CLASSIFIED TRENDS: {len(answers)}")
            Utility.log(answers)        

            # Extract game features from video
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(keywords),
            #             metadata: {
            #               feature_type: str(feature_type)
            #             }
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(feature_type),
            #             metadata: {
            #                 keyword: str(keywords),
            #                 video_frame: int
            #             }
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.EXTRACT_VIDEO_FEATURES)
            
            unique_trends = Utility.get_unique_answers_by_field(answers, "keyword")
            questions = [TextQuestion(text=unique_trend.metadata["keyword"], metadata={
                "feature_type": unique_trend.text}) for unique_trend in unique_trends]
            componentData.questions.extend(questions) 
            answers_detected_game_features = vlm_gaming.get_game_features(componentData.questions)
            componentData.answers.extend(answers_detected_game_features)

            print(f"TOTAL DETECTED OBJECTS: {len(answers_detected_game_features)}")
            Utility.log(answers_detected_game_features)
            
            # Generate feedback report
            # Questions follow the structure:
            # {
            #     [
            #         {
            #             text: str(keywords),
            #             metadata: {
            #               sentiment: str(sentiment),
            #               feature_type: str(feature_type)
            #               is_demanded: boolean
            #             }
            #         }
            #     ]
            # }
            # Answers follow the structure: 
            # {
            #     [
            #         {
            #             text: str(),
            #             metadata: {}
            #             score: float
            #         } 
            #     ]
            # }
            componentData.set_operation(Operation.CREATE_FEEDBACK_REPORT)
            
            provided_reviews: List[Review] = list()
            for answer_detected_game_feature in answers_detected_game_features:
                review_text = answer_detected_game_feature.metadata["video_frame"]
                persisted_review = next((provided_review for provided_review in provided_reviews if provided_review.text == review_text), None)
                
                trend_name = answer_detected_game_feature.metadata["keyword"]
                trend = Trend(trend_name)
                trend.feature_type = FEATURE[answer_detected_game_feature.text.upper()]
                
                if not persisted_review:
                    persisted_review = Review(review_text,
                                Utility.GLOBALS.genre,
                                PLATFORM.UNKNOWN,
                                SOURCE_TYPE.UNKNOWN,
                                Utility.GLOBALS.focus)
                    db_review = DB.get_review_by_trend_name(trend_name)
                    persisted_review.sentiment = db_review.sentiment if db_review else REVIEW_SENTIMENT.NEUTRAL
                
                trend.review = persisted_review
                persisted_review.trends.append(trend)
                provided_reviews.append(persisted_review)
                
            demanded_reviews: List[Review] = [db_review for db_review in DB.reviews if db_review.trends and 
                                              db_review.sentiment != REVIEW_SENTIMENT.UNKNOWN]
            
            reportdata = create_report_data(provided_reviews, demanded_reviews)
            folder_path = config["report"]["path"]
            output_filepath = f"{folder_path}/{Utility.GLOBALS.focus.value[0]}_report_{int(datetime.now().timestamp())}.pdf"
            ScriptManager.generate_pdf(output_filepath, reportdata)

            print(f"REPORT GENERATED IN: {output_filepath}")
            Utility.log(reportdata)

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


            
            
