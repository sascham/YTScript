import os

# Function to list all available channels (directories) in the 'scripts' folder
def list_channels():
    scripts_dir = 'scripts'
    if not os.path.exists(scripts_dir):
        return []
    channels = [
        d for d in os.listdir(scripts_dir)
        if os.path.isdir(os.path.join(scripts_dir, d)) and d != 'Single Videos'
    ]
    # If "Single Videos" directory exists, include it in the list
    if os.path.exists(os.path.join(scripts_dir, 'Single Videos')):
        channels.append('Single Videos')
    return channels

# Function to get the number of individual transcripts for a channel
def get_channel_script_count(channel_name):
    if channel_name == 'Single Videos':
        channel_dir = os.path.join('scripts', 'Single Videos')
    else:
        channel_dir = os.path.join('scripts', channel_name)
    if not os.path.exists(channel_dir):
        return 0
    transcript_files = [
        f for f in os.listdir(channel_dir)
        if os.path.isfile(os.path.join(channel_dir, f)) and f.endswith('.txt') and not f.startswith('combined_')
    ]
    return len(transcript_files)

# Function to get the number of combined transcripts for a channel
def get_combined_script_count(channel_name):
    if channel_name == 'Single Videos':
        combined_dir = os.path.join('scripts', 'Single Videos', 'combined')
    else:
        combined_dir = os.path.join('scripts', channel_name, 'combined')
    if not os.path.exists(combined_dir):
        return 0
    combined_files = [
        f for f in os.listdir(combined_dir)
        if os.path.isfile(os.path.join(combined_dir, f)) and f.endswith('.txt')
    ]
    return len(combined_files)