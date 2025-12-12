from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Pressed pause button isn't the right size
# Update the button sizes and positions on home.py (play, resume, options, credits)
# Update the blurred background image to the one on home.py
# Update login and register pages (some kind of ceiling on login label which binds it and the input fields from reaching a certain height)
# Debug game logic and visuals (check resume_game, reset, and home.py)
# Add api.py and integrate it
# Carousel centering is good enough for now, recalculate later
# Note: When the CarouselSelector's width is increased, it remains that way until the app is closed. Investigate later.

if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()
