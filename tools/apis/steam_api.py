#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
from innovation.FeedbackerAi.tools.utilities import Utility
import requests

def get_game_reviews(app_id, api_key):
    url = f'https://store.steampowered.com/appreviews/{app_id}?json=1'
    headers = {
        'User-Agent': 'Steam Review Fetcher'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        reviews = response.json()
        for review in reviews['reviews'][:5]:  # Show first 5 reviews
            print(f"Rating: {'Upvote' if review['voted_up'] else 'Downvote'}")
            print(f"Review: {review['review']}\n")
    else:
        print(f"Failed to fetch reviews. Status code: {response.status_code}")
        
def main():
    parser = argparse.ArgumentParser(
        description='Youtube API CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Command Comments
    comments_parser = subparsers.add_parser('comments', help='Search for comments')
    comments_parser.add_argument('search_text', type=str, help='Search query for videos')
    comments_parser.add_argument('--max_results', type=int, default=3,
                        help='Maximum number of comments to fetch')

    
    # Command Download
    download_parser = subparsers.add_parser('download', help='Download videos based on search, resolution, and duration')

    download_parser.add_argument('search_text', type=str, help='Search query for videos')
    download_parser.add_argument('--max_results', type=int, default=3,
                        help='Maximum number of videos to fetch')
    download_parser.add_argument('--resolution', type=str, default='240x426',
                        help='Maximum resolution height (e.g., 720)')
    download_parser.add_argument('--max_duration', type=int, default=5,
                        help='Maximum video duration in minutes')
    download_parser.add_argument('--uploaded_days_ago', type=int, default=0,
                        help='Number of days ago when the video was uploaded')
    download_parser.add_argument('--output_path', type=str, default=os.getcwd(),
                        help='Folder path to store videos')

    args = parser.parse_args()
    
    if args.command == 'comments':
        main_comments(args.input)
    elif args.command == 'download':
        main_download(args.input)
    
    sys.exit(0)


if __name__ == "__main__":
    main()


