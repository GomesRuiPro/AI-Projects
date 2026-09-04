from googletrans import Translator
from innovation.FeedbackerAi.tools.local.utilities import Utility
import os
import sys
import argparse
import asyncio

translator = None

class TimeoutExpired(Exception):
    pass

class SubprocessError(Exception):
    pass

async def detect_language(text):
    global translator
    detection = await translator.detect(text)
    language = detection.lang
    return language

async def translate(text, trg_lang='en'):
    global translator
    translation = await translator.translate(text, dest=trg_lang) # The translator will always detect its language before translating. If text in EN and Target lang is also EN, the original text is sent and nothing is translated
    return translation
    
def main():
    global translator
    parser = argparse.ArgumentParser(
        description='Google Translator API CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Command Detect
    detect_parser = subparsers.add_parser('detect', help='Detect language of a text')
    detect_parser.add_argument('text', type=str, help='Text to be detected')
    
    # Command Translate
    translate_parser = subparsers.add_parser('translate', help='Translate the text to a specifig language')

    translate_parser.add_argument('text', type=str, help='Text to be translated')
    translate_parser.add_argument('--trg_lang', type=str, default='en',
                        help='The language you wish to translate to')
    translate_parser.add_argument('--list_separator', type=str, default='',
                        help='For batching')
        
    args = parser.parse_args()
    
    results = ""
    try:
        translator = Translator()
        if args.command == 'detect':
            results = asyncio.run(detect_language(args.text))
                                        
            if not results:
                raise SubprocessError("No results found!")
            
        elif args.command == 'translate':
            text: str = args.text
            if args.list_separator:
                text = text.split(args.list_separator)
            results = asyncio.run(translate(text, args.trg_lang))
                                        
            if not results:
                raise SubprocessError("No results found!")
        
            if isinstance(results, list):
                results = args.list_separator.join([result.text for result in results])
            else:
                results = results.text       
        
    except Exception as ex:
        print(f"An error occurred in translator for text {args.text}: {ex}", file=sys.stderr)
        sys.exit(1)

    print(results)
    sys.exit(0)


if __name__ == "__main__":
    main()