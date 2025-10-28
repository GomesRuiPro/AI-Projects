import re
import os
import sys
from innovation.FeedbackerAi.agents.llm import LLMGaming
from innovation.FeedbackerAi.agents.vlm import VLMGaming
from innovation.FeedbackerAi.agents.exception_handler import RetryException, QuitRequestException
from innovation.FeedbackerAi.tools.local.utilities import Utility
from innovation.FeedbackerAi.tools.local.entities.feature_type import TYPE as FEATURE_TYPE
from innovation.FeedbackerAi.tools.local.dtos.source_type import SOURCE_TYPE
import traceback
from innovation.FeedbackerAi.tools.local.memory.cache import CacheClient
from typing import List

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
    f"\tf=<focus> - to focus on a specific topic: {FEATURE_TYPE._member_names_}\n"
    f"\ts=<source> - to specify which source should we use to validate your game: {SOURCE_TYPE._member_names_}\n"
    "> start "
)

QUESTION_TEMPLATE = (
    "\nDo you want to ask anything else? As a reminder, here are some keys you can use:\n"
    "\tq - to quit\n"
    f"\tf=<focus> - to focus on a specific topic: {FEATURE_TYPE._member_names_}\n"
    f"\ts=<source> - to specify which source should we use to validate your game: {SOURCE_TYPE._member_names_}\n"
    "> start "
)

# Globals
question = None
video_filename = None


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

# def filter_trends(keywords: List[str], feature_type: FEATURE_TYPE = FEATURE_TYPE.GENERAL):   
#        return feature_type.filter(keywords)


def main():
    global question, force_retrain, video_filename, force_download_videos

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
                feature_type = getattr(FEATURE_TYPE, focus) if focus else FEATURE_TYPE.GENERAL
                source_type = getattr(SOURCE_TYPE, source) if source else SOURCE_TYPE.UNKNOWN
            except ValueError as ex:
                raise RetryException

            # Classify genre using VLM
            genre = vlm_gaming.extract_genre(video_filename_path)
            
            # Get popular games
            popular_games = llm_gaming.get_popular_games(genre)
            print(popular_games)

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

            reviews = llm_gaming.get_reviews(popular_games)
            print(reviews)
            
            genre_comments = []
            for review_game in reviews.values():
                for review_game_platform in review_game.values():
                    for review_game_platform_source in review_game_platform:
                        for review_game_platform_source_comments in review_game_platform_source.values():
                            genre_comments.extend(review_game_platform_source_comments)
            
            # # Translate reviews
            # # Translations follow the structure: [comments]
            # translated_genre_comments = llm_gaming.translate_comments(genre_comments)
            # print(translated_genre_comments)
            
            # Get sentiment for review
            # Sentiments follow the structure: {
                # Sentiment: [comments]
            # }
            sentiments = llm_gaming.get_sentiment_score(genre_comments)
            print(sentiments)
            
            # Get keywords for each sentimented review
            # Sentiments follow the structure: {
                # Sentiment: [keywords]
            # }
            sentiments_with_trends = {}
            for sentiment, comments in sentiments.items():
                trends = llm_gaming.get_trends(comments)
                sentiments_with_trends[sentiment] = trends
            print(sentiments_with_trends)
            
            # Filter keywords
            filtered_trends = llm_gaming.filter_trends(Utility.merge_dict_values_to_list(sentiments_with_trends), feature_type)
            
            # Extract object features from video
            detected_objects = vlm_gaming.execute(video_filename_path, filtered_trends)
            print(detected_objects)

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
