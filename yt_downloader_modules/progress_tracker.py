# progress_tracker.py

# Global variables to track progress
checked_videos = 0
completed_videos = 0

def update_checked_videos():
    """Increment the checked videos counter."""
    global checked_videos
    checked_videos += 1

def update_completed_videos():
    """Increment the completed videos counter."""
    global completed_videos
    completed_videos += 1

def reset_progress():
    """Reset progress counters."""
    global checked_videos, completed_videos
    checked_videos = 0
    completed_videos = 0

def get_progress():
    """Return the current progress of checked and completed videos."""
    return checked_videos, completed_videos