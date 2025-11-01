import re
import os
import sys
from innovation.FeedbackerAi.agents.llm import LLMGaming
from innovation.FeedbackerAi.agents.vlm import VLMGaming
from innovation.FeedbackerAi.agents.exception_handler import RetryException, QuitRequestException
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.local.entities.feature import FEATURE
from innovation.FeedbackerAi.tools.local.entities.genre import GENRE
from innovation.FeedbackerAi.tools.local.entities.platform import PLATFORM
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
import traceback
from innovation.FeedbackerAi.tools.local.memory.cache import CacheClient
from typing import List
from innovation.FeedbackerAi.tools.local.entities.review import Review, Trend
import itertools
import argparse
from innovation.FeedbackerAi.tools.local.logger.logger import LoggerFactory
import logging

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
    f"\ts=<source> - to specify which source should we use to validate your game: {[name.lower() for name in SOURCE_TYPE.__members__.keys()]}\n"
    "> start "
)

QUESTION_TEMPLATE = (
    "\nDo you want to ask anything else? As a reminder, here are some keys you can use:\n"
    "\tq - to quit\n"
    f"\tf=<focus> - to focus on a specific topic: {[name.lower() for name in FEATURE.__members__.keys()]}\n"
    f"\ts=<source> - to specify which source should we use to validate your game: {[name.lower() for name in SOURCE_TYPE.__members__.keys()]}\n"
    "> start "
)

# Globals
question = None
video_filename = None
genre = None
feature_type = None
source_type = None


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
    source = None

    parts = input_str.strip().split()

    for part in parts:
        if "f=" in part:
            focus = re.split(r"f=", part, 1)[1]
        elif "s=" in part:
            source = re.split(r"s=", part, 1)[1].split(",")

    
    return focus, source

def map_from_dict(sources_reviews: dict):
    global genre, feature_type, source_type
    reviews: List[Review] = []
    for review_game in sources_reviews.values():
        for review_game_platform_key, review_game_platform_value in review_game.items():
            for review_game_platform_source in review_game_platform_value:
                for review_game_platform_source_comments_key, review_game_platform_source_comments_value in review_game_platform_source.items():
                    for review_game_platform_source_comment in review_game_platform_source_comments_value:
                        _source_type = SOURCE_TYPE[review_game_platform_source_comments_key]
                        _genre = GENRE[genre.upper()]
                        _platform = PLATFORM[review_game_platform_key]
                        _feature_type = FEATURE[feature_type.name]
                        review: Review = Review(review_game_platform_source_comment,
                                                _source_type,
                                                _genre,
                                                _platform,
                                                _feature_type)
                        reviews.append(review)
    return reviews

def print_reviews(reviews: List[Review], exclude_vars = [], include_vars = [], verbose = True):
    print(f"TOTAL REVIEWS: {len(reviews)}")
    [review.print(exclude_vars = exclude_vars, include_vars=include_vars) for review in reviews]

# def filter_trends(keywords: List[str], feature_type: FEATURE_TYPE = FEATURE_TYPE.GENERAL):   
#        return feature_type.filter(keywords)


def main():
    global question, force_retrain, video_filename, force_download_videos, genre, feature_type, source_type
    
    parser = argparse.ArgumentParser(
        description='FeedbackerAI CLI Tool')
    
    parser.add_argument('--verbose', default=False, action='store_true', help='sets log level to DEBUG')
    
    args = parser.parse_args()
    if args.verbose:
        LoggerFactory.logger.get(level=logging.DEBUG)

    question, video_filename = hello(GREETING_TEMPLATE, to_continue=False)

    workflow_config = config['main']['workflow']
    vlm_gaming = VLMGaming(workflow_config)
    llm_gaming = LLMGaming(workflow_config)
    
    # llm_gaming.start_model("with_conversation", "with_source_games")
    # vlm_gaming.start_model("with_object", "with_video_classification")

    while True:
        try:
            
            # Get input
            video_filename_path = os.path.join(TESTING_PATH, video_filename)
            focus, source = parse_user_input(question)
            try: 
                feature_type = FEATURE[focus] if focus else FEATURE.GENERAL
                source_type = SOURCE_TYPE[source] if source else SOURCE_TYPE.ALL
            except ValueError as ex:
                raise RetryException

            # Classify genre using VLM
            genre = vlm_gaming.extract_genre(video_filename_path)
            print(f"GENRE: {genre}")
            
            # Get popular games
            popular_games = llm_gaming.get_popular_games(genre)
            print(f"TOTAL GAMES: {len(popular_games)}")
            Utility.log(popular_games)

            # Get Reviews
            # Reviews follow the structure: {
                # game: {
                    # [webpages:
                        # platform: {
                            # source_type: {
                                # [comments]
                            # } 
                        # }
                    # ]
                # }
            # }
            sources_reviews = llm_gaming.get_reviews(popular_games)            
            reviews: List[Review] = map_from_dict(sources_reviews)
            print_reviews(reviews)
            
            # # Translate reviews
            # # Translations follow the structure: [comments]
            # translated_genre_comments = llm_gaming.translate_comments(genre_comments)
            # print(translated_genre_comments)
            
            # Get sentiment for review
            # Sentiments follow the structure: {
                # Sentiment: [comments]
            # }
            llm_gaming.set_sentiment_score(reviews)
            print_reviews(reviews, include_vars=['id', 'sentiment', 'text'])
            
            # Get keywords for each sentimented review
            # Sentiments follow the structure: {
                # Sentiment: [keywords]
            # }
            llm_gaming.set_trends(reviews)  
            print_reviews(reviews, include_vars=['id', 'sentiment', 'trends'])
            
            # Classify keywords
            merged_trends = list(itertools.chain.from_iterable(review.trends for review in reviews))
            print(f"TOTAL TRENDS: {len(merged_trends)}")

            llm_gaming.classify_trends(reviews, feature_type)
            print_reviews(reviews, include_vars=['id', 'sentiment', 'text'])
                        
            # Extract object features from video
            # detected_objects = vlm_gaming.execute(video_filename_path, trends_classified)
            # print(detected_objects)

            # Ask if user wants to continue or ask something else
            question, video_filename = hello(QUESTION_TEMPLATE)
        except RetryException as ex:
            print(f"Error found: {ex}\n Please try again...")
            traceback.print_exc()
            question, video_filename = hello(QUESTION_TEMPLATE)
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
