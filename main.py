import os

from assets import extract_video, extract_assets

"""
    Current bugs:
        - The background music's MediaPlayer restarts when entering OptionsScreen because 
            on_enter() stops the current and triggers a new MediaPlayer instance even
            when the music currently playing is the same as the one selected in the music_selector
"""

# Before running the file: 
#   run .venv\Scripts\Activate.ps1
#   run python -m uvicorn api:app --reload
#   do Ctrl + Alt + N in main.py
#   open venv in new terminal
if __name__ == "__main__":
    extract_video()
    extract_assets()

    from app import BibleTriviaApp
    app = BibleTriviaApp()
    if os.path.exists("temp_assets"):
        app.run()