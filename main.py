from assets import extract_video, extract_assets
from app import BibleTriviaApp

# If the user fails, the resume button sends them back to Round 1. Make it so that it doesn't appear at all.
    # Not enough information to replicate the bug.
# Add api.py and integrate it
# Carousel centering is good enough for now, recalculate later

# LOW-PRIORITY BUGS:
# Note: When the CarouselSelector's width is increased, it remains that way until the app is closed.
    #  Investigate later.
# Right-clicking on home screen draws red dots that prevent widget functions unless they are clicked again
    # Low priority - likely just smtn to do with Kivy's backend
# Not a bug. There is likely a lot of unnecessary calls to update_lives_display across quiz.py and home.py.


if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()