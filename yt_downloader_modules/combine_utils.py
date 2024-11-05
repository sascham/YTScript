import os
from datetime import datetime

def combine_transcripts(channel_dir, channel_name):
    max_size = 19 * 1024 * 1024  # 19 MB in bytes
    combined_dir = os.path.join(channel_dir, 'combined')
    os.makedirs(combined_dir, exist_ok=True)

    transcript_files = [
        os.path.join(channel_dir, f) for f in os.listdir(channel_dir)
        if os.path.isfile(os.path.join(channel_dir, f)) and f.endswith('.txt') and not f.startswith('combined_')
    ]

    if not transcript_files:
        print(f"No transcript files found in {channel_dir}")
        return

    # Get the current date in 'MMMDD' format
    date_str = datetime.now().strftime('%b%d')
    combined_filename = f"{channel_name}_{date_str}.txt"
    combined_filepath = os.path.join(combined_dir, combined_filename)

    current_size = 0
    combined_content = ''
    
    for filepath in transcript_files:
        file_size = os.path.getsize(filepath)
        
        # If adding this file exceeds max size, stop adding more content
        if current_size + file_size > max_size:
            print(f"Warning: Combined content exceeds 19MB limit. Stopping at {combined_filename}.")
            break

        # Append current file content to combined content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_content += content + '\n\n'

        current_size += file_size
        os.remove(filepath)  # Remove the individual file after combining

    # Write all combined content to a single file
    with open(combined_filepath, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    print(f"Created combined file: {combined_filepath}")