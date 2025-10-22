#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import Optional, Dict, Any

# Load configuration
config = Utility.load_yaml()["apis"]["google"]
YOUTUBE_API_KEY = config["youtube-key"]
MAX_ATTEMPTS = config.get('max_number_attempts', 5)
DAYS_BETWEEN_ATTEMPTS = config.get('video_published_before_days', 3)
IS_SIMPLE_QUERY = config.get('is_simple_query', True)
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_video_urls(query, duration_limit_minutes, uploaded_days_ago=0, max_query_results=3):
    valid_video_urls = []
    search_response = search_videos(query, duration_limit_minutes, uploaded_days_ago, max_query_results)
    
    # Map video IDs to publishedAt dates
    base_url = 'https://www.youtube.com/watch?v='
    valid_video_urls = [base_url + item['id']['videoId']
                        for item in search_response['items']]
    
    return valid_video_urls

def get_video_comments(query, duration_limit_minutes, uploaded_days_ago=0, max_query_results=3):
    comments = []
    search_response = search_videos(query, duration_limit_minutes, uploaded_days_ago, 1)
    
    video_id = search_response['items'][0]['id']['videoId']
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=max_query_results,
        textFormat='plainText'
    )

    while request:
        response = request.execute()
        
        # Sort comments by popularity
        sorted_comments = sorted(response.get('items', []), key=lambda c: c.get('likeCount', 0), reverse=True)
        
        for item in sorted_comments:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'published_at': comment['publishedAt']
            })
        # Check if there is a next page
        request = youtube.commentThreads().list_next(request, response)
    return comments
    
def search_videos(query, duration_limit_minutes, uploaded_days_ago=0, max_query_results=3):
    """
    Search for videos matching the query and filter by duration and upload date.
    """

    # Search for videos
    videoDuration = 'short' if duration_limit_minutes <= 4 else 'medium'
    publishedAfter = datetime.now(timezone.utc) - timedelta(days=MAX_ATTEMPTS *
                                                            DAYS_BETWEEN_ATTEMPTS) if not uploaded_days_ago else datetime.now(timezone.utc) - timedelta(days=uploaded_days_ago)

    request_params = {
        'q': query,
        'part': 'id',
        'eventType': 'completed',
        'maxResults': max_query_results,
        'videoCaption': 'any',
        'videoDefinition': 'any',
        'type': 'video',
        'videoCategoryId': 20,
        'safeSearch': 'none',
        'order': 'relevance',
        'videoDimension': 'any',
        'videoDuration': videoDuration,
        'publishedAfter': publishedAfter.isoformat().replace('+00:00', 'Z'),
        'videoEmbeddable': 'any',
        'videoSyndicated': 'true',
        'videoLicense': 'youtube'
    }

    request = youtube.search().list(**request_params)
    search_response = request.execute()

    return search_response

    # published_at_map = {
    #     item['id']['videoId']: item['snippet']['publishedAt']
    #     for item in search_response['items']
    # }

    # if not video_ids:
    #     return []

    # Get video details
    # video_response = youtube.videos().list(
    #     id=','.join(video_ids),
    #     part='contentDetails'
    # ).execute()

    # valid_video_urls = []

    # for video in video_response['items']:
    #     video_id = video['id']
    # published_at_str = published_at_map.get(video_id)
    # if is_video_valid(video, published_at_str, duration_limit_minutes, uploaded_days_ago):
    # valid_video_urls.append(base_url + video_id)



def is_video_valid(details, published_at_str, duration_limit_minutes, uploaded_days_ago=None):
    """
    Validate video based on duration, license, and upload date.
    """
    duration_seconds = Utility.iso_duration_to_seconds(
        details['contentDetails']['duration'])
    duration_minutes = duration_seconds / 60

    # Check duration
    if duration_minutes > duration_limit_minutes:
        return False

    # Check license
    if not details.get('contentDetails', {}).get('licensedContent', False):
        return False

    # Check upload date
    if uploaded_days_ago is not None and published_at_str:
        published_at = Utility.str_to_datetime(published_at_str)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=uploaded_days_ago)
        if published_at > cutoff_date:
            return False

    return True


def download_video(video_url, format_ext, output_path, resolution):
    """
    Download the video with specified format and resolution.
    """
    ydl_opts = {
        'format': f'bestvideo[resolution={resolution}]+bestaudio/best',
        'noplaylist': True,
        'restrictfilenames': True,
        'quiet': True,
        'merge_output_format': format_ext,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        print(
            f"Finished downloading {video_url} [{resolution} - {format_ext}] to {output_path}!")


def get_output_format(video_url, resolution, req_formats=['mp4', 'avi']):
    """
    Determine the available format matching requirements.
    """
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        for fmt in info.get('formats', []):
            if fmt.get('ext') in req_formats and fmt.get('resolution') == resolution:
                return fmt.get('ext')
    return None

def main_comments(args):
    max_query_results = len(args.search_text.split(
    "OR")) if "OR" in args.search_text else 1
    init_search_text = f"{args.search_text} that lasts no longer than {args.max_duration} minutes" if not IS_SIMPLE_QUERY else args.search_text
    search_text = init_search_text
    uploaded_days_ago = args.uploaded_days_ago
    comments_fetched = 0
    
    try:
        while True:
            print(f"Trying with search: '{search_text}'...")

            # Search videos
            max_query_results = max_query_results - comments_fetched
            videos_urls = search_videos(
                search_text,
                args.max_duration,
                uploaded_days_ago=uploaded_days_ago,
                max_query_results=max_query_results
            )
            
            
    except Exception as e:
        print(f"Error occurred: {e}")
        if "Temporary failure" in str(e):
            sys.exit(2)
        if "Unable to connect to proxy" in str(e):
            print("You need to connect to the Ubisoft VPN!")
        sys.exit(1)
        
def main_download(args):
    max_query_results = len(args.search_text.split(
    "OR")) if "OR" in args.search_text else 1
    init_search_text = f"{args.search_text} that lasts no longer than {args.max_duration} minutes" if not IS_SIMPLE_QUERY else args.search_text
    search_text = init_search_text
    videos_downloaded = 0
    uploaded_days_ago = args.uploaded_days_ago
    try:
        while True:
            print(f"Trying with search: '{search_text}'...")

            # Search videos
            max_query_results = max_query_results - videos_downloaded
            videos_urls = search_videos(
                search_text,
                args.max_duration,
                uploaded_days_ago=uploaded_days_ago,
                max_query_results=max_query_results
            )

            # Download each video
            for video_url in videos_urls:
                format_ext = get_output_format(video_url, args.resolution)
                if format_ext:
                    download_video(video_url, format_ext,
                                   args.output_path, args.resolution)
                    videos_downloaded += 1

            # Check termination conditions
            if videos_downloaded >= args.max_results or uploaded_days_ago >= (MAX_ATTEMPTS * DAYS_BETWEEN_ATTEMPTS) + args.uploaded_days_ago:
                break

            # Increase days range and update search query for next iteration
            uploaded_days_ago += DAYS_BETWEEN_ATTEMPTS
            if not IS_SIMPLE_QUERY:
                search_text = f"{init_search_text} from the last {uploaded_days_ago} days"

        if videos_downloaded == 0:
            print("No videos downloaded.")
            sys.exit(2)

    except Exception as e:
        print(f"Error occurred: {e}")
        if "Temporary failure" in str(e):
            sys.exit(2)
        if "Unable to connect to proxy" in str(e):
            print("You need to connect to the Ubisoft VPN!")
        sys.exit(1)

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
