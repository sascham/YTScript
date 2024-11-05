import os
import re
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    NoTranscriptAvailable,
)
from .video_utils import sanitize_filename, get_video_info, get_channel_video_ids, extract_video_id
from datetime import datetime, timedelta
from .progress_tracker import update_checked_videos, update_completed_videos, completed_videos

# Global list to store log messages
log_messages = []

# Function to immediately push log messages to simulate real-time updates
def push_log_message(message):
    log_messages.append(message)

# Download transcript for a single video
def download_transcript(video_info, output_dir):
    video_id = video_info['id']
    title = video_info['title']
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        transcript_data = transcript.fetch()
        
        # Combine all transcript pieces and add line breaks
        formatted_text = '\n'.join([item['text'] for item in transcript_data])
        
        # Write the formatted text to file
        filename = sanitize_filename(f"{title}.txt")
        filepath = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        push_log_message(f"Transcript saved: {filepath}")
        update_completed_videos()  # Update completed downloads
    except (NoTranscriptFound, TranscriptsDisabled, NoTranscriptAvailable):
        push_log_message(f"No transcript available for video: {title}")
    except Exception as e:
        push_log_message(f"Error downloading transcript for {title}: {e}")

# Download all transcripts for a channel
def download_transcripts(channel_input, months=None):
    global log_messages
    log_messages.clear()  # Clear previous logs

    if channel_input.startswith('http'):
        channel_url = channel_input
    elif channel_input.startswith('@'):
        channel_url = f'https://www.youtube.com/{channel_input}/videos'
    elif re.match(r'^[A-Za-z0-9_-]{24}$', channel_input):
        channel_url = f'https://www.youtube.com/channel/{channel_input}/videos'
    else:
        channel_url = f'https://www.youtube.com/c/{channel_input}/videos'

    push_log_message(f"Retrieving video list from the channel: {channel_input}")
    push_log_message(f"Constructed channel URL: {channel_url}")

    try:
        channel_title, video_ids = get_channel_video_ids(channel_url)
    except Exception as e:
        push_log_message(f"Error getting video list: {e}")
        return log_messages

    if not channel_title:
        push_log_message("Failed to retrieve channel information.")
        return log_messages

    push_log_message(f"Channel Title: {channel_title}")
    push_log_message(f"Total videos found: {len(video_ids)}")

    output_dir = os.path.join('scripts', sanitize_filename(channel_title))
    os.makedirs(output_dir, exist_ok=True)

    if not video_ids:
        push_log_message("No videos found.")
        return log_messages

    if months is not None:
        months_ago = datetime.now() - timedelta(days=months * 30)
    else:
        months_ago = None

    videos_to_download = []
    stop_checking = False

    def process_video(video_id):
        nonlocal stop_checking
        if stop_checking:
            return None
        video_info = get_video_info(video_id)
        if not video_info:
            push_log_message(f"Skipping video ID {video_id} due to missing metadata.")
            return None
        if months_ago and video_info.get('upload_date'):
            upload_date_str = video_info['upload_date']
            upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
            if upload_date < months_ago:
                push_log_message(f"Skipping video '{video_info['title']}' as it's older than specified months.")
                stop_checking = True  # Stop further checking after encountering an older video
                return None
        push_log_message(f"Checked video: {video_info['title']}")
        update_checked_videos()
        return video_info

    for vid_id in video_ids:
        video_info = process_video(vid_id)
        if video_info:
            videos_to_download.append(video_info)

    push_log_message(f"Videos after filtering: {len(videos_to_download)}")

    if not videos_to_download:
        push_log_message("No videos found after applying the filter.")
        return log_messages

    for video in videos_to_download:
        download_transcript(video, output_dir)

    push_log_message("Download completed.")
    return log_messages

# Download transcript for a single video (external function)
def download_single_video_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise Exception("Invalid video URL")
    video_info = get_video_info(video_id)
    if not video_info:
        raise Exception("Failed to retrieve video information.")

    output_dir = os.path.join('scripts', 'Single Videos')
    os.makedirs(output_dir, exist_ok=True)
    download_transcript(video_info, output_dir)
    update_completed_videos()