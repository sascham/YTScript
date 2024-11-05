from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import re
import shutil
from yt_downloader_modules.video_utils import (
    get_total_videos,
    extract_video_id,
    get_channel_video_ids
)
from yt_downloader_modules.transcript_utils import (
    download_transcripts,
    download_single_video_transcript,
    log_messages
)
from yt_downloader_modules.channel_utils import (
    list_channels,
    get_channel_script_count,
    get_combined_script_count,
)
from yt_downloader_modules.combine_utils import (
    combine_transcripts,
)
from yt_downloader_modules.progress_tracker import (
    checked_videos,
    completed_videos,
    reset_progress
)
import threading

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'

# Global variables to track progress and logs
total_videos = 0

def is_video_url(url):
    video_url_patterns = [
        r'^https?://(www\.)?youtube\.com/watch\?v=',
        r'^https?://youtu\.be/',
    ]
    for pattern in video_url_patterns:
        if re.match(pattern, url):
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        channel_input = request.form.get('channel_input')
        months = request.form.get('months')
        if months == 'all':
            months = None
        else:
            months = int(months)

        global total_videos, log_messages
        total_videos = 0
        reset_progress()
        log_messages.clear()  # Clear previous logs at the start of a new download

        try:
            if is_video_url(channel_input):
                total_videos = 1
                thread = threading.Thread(target=download_single_video_transcript, args=(channel_input,))
                thread.start()
                flash(f'Transcript downloaded for video: {channel_input}', 'success')
                return redirect(url_for('channels'))
            else:
                total_videos = get_total_videos(channel_input, months)
                log_messages.append(f"Total videos found: {total_videos}")
                thread = threading.Thread(target=download_transcripts_with_logging, args=(channel_input, months))
                thread.start()
                return render_template('download_progress.html', total_videos=total_videos)
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('download'))

    return render_template('download.html')

def download_transcripts_with_logging(channel_input, months):
    """Wrapper around download_transcripts to add logging."""
    global log_messages
    log_messages.append(f"Starting download for channel: {channel_input} with month filter: {months}")
    
    try:
        videos = get_channel_video_ids(channel_input)

        for video in videos:
            if video is None or 'id' not in video or 'title' not in video:
                video_id = video.get('id', 'Unknown ID') if video else 'None'
                log_messages.append(f"Skipping video ID {video_id} due to missing metadata.")
                continue
            log_messages.append(f"Processing video ID {video['id']} with title: {video['title']}")
        
        download_transcripts(channel_input, months)
        log_messages.append("Download completed.")
    except Exception as e:
        log_messages.append(f"Error occurred: {str(e)}")

@app.route('/progress')
def progress():
    global checked_videos, completed_videos, total_videos, log_messages
    print("Log Messages:", log_messages)  # Add this line to verify backend output
    return jsonify({
        'checked_videos': checked_videos,
        'completed_videos': completed_videos,
        'total_videos': total_videos,
        'log_messages': log_messages
    })

@app.route('/channels')
def channels():
    channels_list = list_channels()
    channel_info = []
    for channel in channels_list:
        script_count = get_channel_script_count(channel)
        combined_script_count = get_combined_script_count(channel)
        can_combine = script_count > 0
        channel_info.append({
            'name': channel,
            'script_count': script_count,
            'combined_script_count': combined_script_count,
            'can_combine': can_combine
        })
    return render_template('channels.html', channels=channel_info)

@app.route('/combine/<channel_name>')
def combine_channel(channel_name):
    try:
        if channel_name == 'Single Videos':
            channel_dir = os.path.join('scripts', 'Single Videos')
        else:
            channel_dir = os.path.join('scripts', channel_name)
        if not os.path.exists(channel_dir):
            flash(f"Channel '{channel_name}' does not exist.", 'danger')
            return redirect(url_for('channels'))
        
        combine_transcripts(channel_dir, channel_name)
        
        flash(f"Transcripts for '{channel_name}' have been combined.", 'success')
    except Exception as e:
        flash(f"Error combining transcripts: {str(e)}", 'danger')
    return redirect(url_for('channels'))

@app.route('/delete_channel/<channel_name>')
def delete_channel(channel_name):
    """Delete the entire channel directory and its contents."""
    try:
        channel_dir = os.path.join('scripts', channel_name)
        if os.path.exists(channel_dir):
            shutil.rmtree(channel_dir)
            flash(f"Channel '{channel_name}' and all files have been deleted.", 'success')
        else:
            flash(f"Channel '{channel_name}' does not exist.", 'danger')
    except Exception as e:
        flash(f"Error deleting channel '{channel_name}': {e}", 'danger')
    return redirect(url_for('channels'))

@app.route('/channel/<channel_name>', methods=['GET', 'POST'])
def view_channel_scripts(channel_name):
    if channel_name == 'Single Videos':
        channel_dir = os.path.join('scripts', 'Single Videos')
    else:
        channel_dir = os.path.join('scripts', channel_name)
    if not os.path.exists(channel_dir):
        flash(f"Channel '{channel_name}' does not exist.", 'danger')
        return redirect(url_for('channels'))

    if request.method == 'POST':
        selected_scripts = request.form.getlist('scripts')
        script_type = request.form.get('script_type')
        if script_type == 'individual':
            for script in selected_scripts:
                script_path = os.path.join(channel_dir, script)
                if os.path.exists(script_path):
                    os.remove(script_path)
            flash(f"Selected individual scripts have been deleted.", 'success')
        elif script_type == 'combined':
            combined_dir = os.path.join(channel_dir, 'combined')
            for script in selected_scripts:
                script_path = os.path.join(combined_dir, script)
                if os.path.exists(script_path):
                    os.remove(script_path)
            flash(f"Selected combined scripts have been deleted.", 'success')
        else:
            flash(f"Invalid script type.", 'danger')
        return redirect(url_for('view_channel_scripts', channel_name=channel_name))

    scripts = [
        f for f in os.listdir(channel_dir)
        if os.path.isfile(os.path.join(channel_dir, f)) and f.endswith('.txt') and not f.startswith('combined_')
    ]

    combined_dir = os.path.join(channel_dir, 'combined')
    combined_scripts = []
    if os.path.exists(combined_dir):
        combined_scripts = [
            f for f in os.listdir(combined_dir)
            if os.path.isfile(os.path.join(combined_dir, f)) and f.endswith('.txt')
        ]

    return render_template(
        'channel_scripts.html',
        channel_name=channel_name,
        scripts=scripts,
        combined_scripts=combined_scripts
    )

@app.route('/download_combined/<channel_name>/<script_name>')
def download_combined_script(channel_name, script_name):
    if channel_name == 'Single Videos':
        combined_filepath = os.path.join('scripts', 'Single Videos', 'combined', script_name)
    else:
        combined_filepath = os.path.join('scripts', channel_name, 'combined', script_name)
    if not os.path.exists(combined_filepath):
        flash(f"File '{script_name}' does not exist.", 'danger')
        return redirect(url_for('view_channel_scripts', channel_name=channel_name))
    return send_file(combined_filepath, as_attachment=True)

@app.route('/download_individual/<channel_name>/<script_name>')
def download_individual_script(channel_name, script_name):
    channel_dir = os.path.join('scripts', channel_name)
    individual_filepath = os.path.join(channel_dir, script_name)
    if not os.path.exists(individual_filepath):
        flash(f"File '{script_name}' does not exist.", 'danger')
        return redirect(url_for('view_channel_scripts', channel_name=channel_name))
    return send_file(individual_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
