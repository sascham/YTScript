import os
import re
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

# Function to sanitize filenames
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# Extract video ID from various YouTube URL formats
def extract_video_id(url):
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'^https?://(?:www\.)?youtube\.com/embed/([^?&]+)',
        r'^https?://(?:www\.)?youtu\.be/([^?&]+)',
    ]
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None

# Get total number of videos in a channel
def get_total_videos(channel_input, months=None):
    if channel_input.startswith('http'):
        channel_url = channel_input
    elif channel_input.startswith('@'):
        channel_url = f'https://www.youtube.com/{channel_input}/videos'
    elif re.match(r'^[A-Za-z0-9_-]{24}$', channel_input):
        channel_url = f'https://www.youtube.com/channel/{channel_input}/videos'
    else:
        channel_url = f'https://www.youtube.com/c/{channel_input}/videos'

    # Print the constructed URL for debugging
    print(f"Constructed URL: {channel_url}")

    try:
        # Get channel title and list of video IDs
        channel_title, video_ids = get_channel_video_ids(channel_url)

        if not channel_title or video_ids is None:
            raise Exception("Failed to retrieve channel information. Check channel URL or availability.")

        total_videos = len(video_ids)
        return total_videos
    except Exception as e:
        print(f"Error in get_total_videos: {str(e)}")
        return 0  # Returning 0 if total cannot be determined due to error

# Get channel video IDs
def get_channel_video_ids(channel_url):
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'extract_flat': 'in_playlist',
        'simulate': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            channel_title = info.get('title', 'channel_transcripts')
            entries = info.get('entries', [])
            video_ids = [entry.get('id') for entry in entries if entry.get('id')]
            return channel_title, video_ids
        except DownloadError as e:
            print(f"Error extracting channel info: {e}")
            return None, []
        except Exception as e:
            print(f"Unexpected error extracting channel info: {e}")
            return None, []

# Get video info based on video ID
def get_video_info(video_id):
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'simulate': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(video_url, download=False)
            video_id = info.get('id')
            title = info.get('title')
            upload_date = info.get('upload_date')  # Format: YYYYMMDD
            return {
                'id': video_id,
                'title': title,
                'upload_date': upload_date,
            }
        except DownloadError as e:
            print(f"Error extracting video info for {video_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for video {video_id}: {e}")
            return None
