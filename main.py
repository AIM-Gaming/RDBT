from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Debug game logic and visuals (check resume_game, reset, and home.py)  # Let people bug test this before moving on
    # Mess with the game and resume logic to ensure it works as intended
# Add api.py and integrate it
# Carousel centering is good enough for now, recalculate later
# Note: When the CarouselSelector's width is increased, it remains that way until the app is closed.
    #  Investigate later.
# Right-clicking on home screen draws red dots that prevent widget functions unless they are clicked again
    # Low priority - likely just smtn to do with Kivy's backend


if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()