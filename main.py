from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Lives display isn't updating correctly for new games.
    # Quiz manager lives updates correctly, but the image doesn't mimic it.
    # reset() isn't called with the True parameter when clicking the quit button at the end of the quiz.
    # quit_quiz() needs proper conditioning for when the quiz is over
        # Right now it always meets the first 'if in_progress' condition
        # Check to see if self.game_over is changed in that method or its parent method confirm_quit().
    # Push come to shove, just set a flag for when quit_quiz() is triggered from the end of the quiz.

# Add api.py and integrate it
# Carousel centering is good enough for now, recalculate later

# LOW-PRIORITY BUGS:
# Note: When the CarouselSelector's width is increased, it remains that way until the app is closed.
    #  Investigate later.
# Right-clicking on home screen draws red dots that prevent widget functions unless they are clicked again
    # Low priority - likely just smtn to do with Kivy's backend


if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()