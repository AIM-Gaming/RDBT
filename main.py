import os

from assets import extract_video, extract_assets
from app import BibleTriviaApp

# The order in which the temporary assets folder is created and the background image file is retrieved is out of order
    # (The file is accessed before the folder is created) Look at when these two events occur.

# LOW-PRIORITY BUGS:
# Carousel centering is good enough for now, recalculate later
    # Note: When the CarouselSelector's width is increased, it remains that way until the app is closed.
# Right-clicking on home screen draws red dots that prevent widget functions unless they are clicked again
    # Likely just smtn to do with Kivy's backend
# Not a bug. There is likely a lot of unnecessary calls to update_lives_display across quiz.py and home.py.

# Before running the file: 
#   run .venv\Scripts\Activate.ps1
#   run python -m uvicorn api:app --reload
#   do Ctrl + Alt + N in main.py
#   open venv in new terminal
if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    if os.path.exists("temp_assets"):
        app.run()