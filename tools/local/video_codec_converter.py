#!/usr/bin/env python3
import os
import argparse
import sys
from innovation.FeedbackerAi.tools.utilities import Utility
import ffmpeg

# Load configuration
config = Utility.load_yaml()["local"]["ffmpeg"]
VIDEO_CODEC = config["video-codec"]
VIDEO_BITRATE = config["video-bitrate"]
AUDIO_CODEC = config["audio-codec"]
AUDIO_BITRATE = config["audio-bitrate"]

class TimeoutExpired(Exception):
    pass

class SubprocessError(Exception):
    pass

def get_video_codec(video_path):
    probe = ffmpeg.probe(video_path)
    video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if video_streams:
        return video_streams[0]['codec_name']
    return None

def convert(video_path, video_converted_path):
    ffmpeg.input(video_path).output(
        video_converted_path, 
        vcodec=VIDEO_CODEC, 
        video_bitrate=VIDEO_BITRATE, 
        acodec='copy', 
        audio_bitrate=AUDIO_BITRATE).run(overwrite_output=True)

def main():
    parser = argparse.ArgumentParser(description='Convert videos based on codecs.')
    parser.add_argument('input_path', type=str, help='Video to be converted path')
    parser.add_argument('--output_path', type=str, default="", help='Video converted path')

    args = parser.parse_args()

    video_path = args.input_path
    video_converted_path = args.output_path 
    if not video_converted_path:
        video_converted_path = Utility.rename_file(video_path, "backup")

    try:
        
        if not Utility.does_file_exist(video_path):
            raise Exception(f"File '{video_path}' does not exist")
        video_codec_received = get_video_codec(video_path)
        if VIDEO_CODEC == video_codec_received  or not args.output_path:
            print(f"Conversion skipped for video file {video_converted_path}...")
            sys.exit(2)
        convert(video_path, video_converted_path)
        Utility.remove_file(video_path)
        
        if not Utility.does_file_exist(video_converted_path) or Utility.does_file_exist(video_path):
            raise Exception(f"Failed to convert from '{video_path}' to '{video_converted_path}'")

    except Exception as e:
        print(f"An error occurred for video file {video_converted_path}: {e}")
        sys.exit(1)

    print(f"Conversion completed for video file {video_converted_path}!")
    sys.exit(0)

if __name__ == "__main__":
    main()
