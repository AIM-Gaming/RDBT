import os

from assets import extract_video, extract_assets

# LOW-PRIORITY BUGS:
# Carousel centering is good enough for now, recalculate later
    # Note: When the CarouselSelector's width is increased, it remains that way until the app is closed.


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