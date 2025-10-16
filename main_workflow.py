import re
import os
import sys
from agents.llm import LLMGaming
from agents.vlm import VLMGaming
from agents.exception_handler import RetryException, QuitRequestException
from tools.utilities import Utility
import traceback
from tools.local.memory.cache import CacheClient

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
    "\tf=<focus> - to focus on a specific topic (by default: general)\n"
    "\ts=<source> - to specify which sources should we use to validate your game (by default: social media)\n"
    "> start "
)

QUESTION_TEMPLATE = (
    "\nDo you want to ask anything else? As a reminder, here are some keys you can use:\n"
    "\tq - to quit\n"
    "\tf=<focus> - to focus on a specific topic (by default: general)\n"
    "\ts=<source> - to specify which sources should we use to validate your game (by default: social media)\n"
    "> start "
)

# Globals
question = None
video_filename = None


def hello(template):
    video_filename = config["main"]['file_game']
    question = None

    while video_filename is None or question is None:
        question = input(template).strip()
        params = question.split(" ")

        if len(params) > 1 and len(params) < 4:
            video_filename = params[0]

        elif len(params) == 1:
            if params[0] == 'q':
                raise QuitRequestException
            else:
                video_filename = params[0] if params[0] else config["main"]['file_game']
        else:
            raise RetryException("Unexpected input data.")

        return question, video_filename


def goodbye():
    print("All good! If you need more help, you know where to find me!")
    print("Note: Keep in mind I am a simple PoC. If you find any errors or want to improve me, contact the developer Rui Gomes.")


def parse_user_input(input_str):
    focus = "general"
    sources = ["social media"]

    parts = input_str.strip().split()

    for part in parts:
        if "f=" in part:
            focus = re.split(r"f=", part, 1)[1]
        elif "s=" in part:
            sources = re.split(r"s=", part, 1)[1].split(",")

    return focus, sources


def main():
    global question, force_retrain, video_filename, force_download_videos

    question, video_filename = hello(GREETING_TEMPLATE)
    use_model_finetuned = config["vlm"]["use_model_finetuned"]
    vlm_gaming = VLMGaming()
    llm_gaming = LLMGaming()
    
    llm_gaming.start_model("with_conversation", "with_source_games")
    vlm_gaming.start_model("with_object", "with_video_classification")

    while True:
        try:
            video_filename_path = os.path.join(TESTING_PATH, video_filename)
            # Get input
            focus, sources = parse_user_input(question)

            # vlm_gaming.start_model(force_retrain=force_retrain, force_download_videos=force_download_videos, use_model_finetuned=use_model_finetuned, games_per_genre=games_per_genre)

            # Classify genre using VLM
            print("Classifying video...")
            genre = vlm_gaming.get_genre(video_filename_path)
            
            # Get popular games
            popular_games = llm_gaming.get_popular_games(genre)
            print(popular_games)

            # Get trends keywords
            # response = llm_gaming.get_trends(genre)
            # print(response)
            
            # Extract features from video
            result = vlm_gaming.execute(video_filename_path)


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
