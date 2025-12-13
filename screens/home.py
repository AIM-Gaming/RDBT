from kivy.app import App
from kivy.uix.screenmanager import Screen, FadeTransition, SlideTransition
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.label import Label

import os
import mysql.connector
from ffpyplayer.player import MediaPlayer

from utils import debug_print, TEMP_ASSETS_DIR, play_sfx, last_logged_in
from db import get_db_connection
from quiz_manager import QuizManager
from widgets.outlined_label import OutlinedLabel


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        
        self.music_path = os.path.join(TEMP_ASSETS_DIR, "music", "Amazing Grace.mp3")
        self.music = None
        self.player = None

        from kivy.core.image import Image as CoreImage
        # Ensure dimensions are 1920x1290
        self.background_texture = CoreImage(os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png")).texture

        self.bg_color = None
        self.bg_rect = None

        with self.layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            self.bg_color = Color(1, 1, 1, 1)  # White color
            self.bg_rect = Rectangle(pos=self.layout.pos, size=self.layout.size)
        
        self.layout.bind(pos=self.update_bg, size=self.update_bg)
        self.update_bg(None, None)
        
        self.quiz_screen = None
        self.quiz_manager = QuizManager(bible_version=App.get_running_app().user_settings.get("bible_version", "NIV"))

        # Flag for resume button
        self.has_left_game_this_session = False

        # Version label
        self.version_label = OutlinedLabel(text=f"v{App.get_running_app().version}", font_size=30, size_hint=(None, None), size=(200, 50), pos_hint={"left": 0.05, "bottom": 0.05}, outline_color=[0, 0, 0, 1], text_color=[1, 1, 1, 1])
        self.layout.add_widget(self.version_label)
        
        # Username label
        self.username_label = OutlinedLabel(text="", font_size=30, size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.15, "top": 0.97}, opacity=0, outline_color=[0, 0, 0, 1], text_color=[1, 1, 1, 1])
        self.layout.add_widget(self.username_label)
        
        # Login button
        self.login_button = Button(size_hint=(None, None),
                                   size=(130, 130),
                                   pos_hint={"center_x": 0.15, "top": 0.95},
                                   opacity=0,
                                   background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButtonIcon.png"),
                                   background_down=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButtonIconPressed.png"),
                                   border=(0, 0, 0, 0),
                                   disabled=True
                                   )
        self.login_button.bind(on_release=self.open_login, texture_size=self.login_button.setter('size'))
        self.layout.add_widget(self.login_button)
        
        # Logout button
        self.logout_button = Button(size_hint=(None, None), pos_hint={"center_x": 0.15, "top": 0.9}, opacity=0,
                                    background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "LogoutButton.png"),
                                    background_down=os.path.join(TEMP_ASSETS_DIR, "images", "LogoutButtonPressed.png"),
                                    border=(0, 0, 0, 0), size=(256, 144)
                                    )
        self.logout_button.bind(on_release=self.logout)
        self.layout.add_widget(self.logout_button)
        
        # Box layout to hold the buttons
        self.button_box = None
        
        self.layout.add_widget(Widget(size_hint=(1, 0.1)))
        self.update_button_box()
        self.layout.add_widget(Widget(size_hint=(1, 0.1)))

    def update_bg(self, instance, value):
        """Forces the background to fill the whole screen"""
        self.bg_rect.texture = self.background_texture
        self.bg_rect.size = self.layout.size
        self.bg_rect.pos = self.layout.pos
    
    def on_enter(self, *args):
        self.quiz_screen = self.manager.get_screen("QuizOne")
        
        current_app = App.get_running_app()
        user_id = current_app.user_id
        last_user = last_logged_in()
        
        if user_id:
            username = last_user.get("username", "User")
            
            # Show username label
            self.username_label.text = f"Welcome {username}!"
            self.username_label.opacity = 100
            self.username_label.size_hint = (None, None)
            self.username_label.size = (200, 50)
            self.username_label.pos_hint = {"center_x": 0.15, "top": 0.97}
            
            # Hide login button
            self.login_button.opacity = 0
            self.login_button.disabled = True
            
            # Show logout button
            self.logout_button.opacity = 100
            self.logout_button.disabled = False
            self.logout_button.size_hint = (None, None)
            self.logout_button.size = (256, 144)
            self.logout_button.pos_hint = {"center_x": 0.15, "top": 0.9}
            
            conn, cursor = get_db_connection()
            
            # Update last login time
            cursor.execute("USE users;")
            cursor.execute("UPDATE users SET last_logged_in = NOW() WHERE id = %s", (user_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
        
        else:
            # Hide username label
            self.username_label.opacity = 0
            self.username_label.size_hint = (None, None)
            self.username_label.size = (0, 0)
            self.username_label.pos_hint = {"center_x": -1, "top": 0.97}
            
            # Show login button
            self.login_button.opacity = 100
            self.login_button.disabled = False
            
            # Hide logout button
            self.logout_button.opacity = 0
            self.logout_button.disabled = True
            self.logout_button.size_hint = (None, None)
            self.logout_button.size = (0, 0)
            self.logout_button.pos_hint = {"center_x": -1, "top": 0.9}
        
        if self.player is None:
            Clock.schedule_once(lambda dt: self.play_music(music_file=current_app.user_settings['background_music']), 0.5)
    
    # noinspection PyUnusedLocal
    def play_music(self, dt=0, reset=False, music_file=None):
        """Starts and resets music player with current-user defined volume settings"""
        debug_print("Starting or restarting music")

        if music_file is None:
            music_file = App.get_running_app().user_settings.get('background_music')
            if not music_file:
                debug_print(f"No defined music path")
                return
        
        try:
            if reset and self.player:  # App has a chance of crashing upon restart
                debug_print("Resetting existing player")
                Clock.unschedule(self.check_player_state)
                
                self.player.set_pause(True)
                self.player.close_player()
                self.player = None
                
                Clock.schedule_once(lambda dt: self.play_music(App.get_running_app().user_settings['background_music']), 1.0)
                return
            
            music_path = os.path.join(TEMP_ASSETS_DIR, "music", music_file)
            if os.path.exists(music_file):
                debug_print("Music file exists")
            
            self.player = MediaPlayer(music_path)
            
            if not self.player:
                debug_print("MediaPlayer failed to initialize.")
                return
            
            debug_print("MediaPlayer initialized")
            current_app = App.get_running_app()
            
            if current_app.user_settings is None:
                current_app.user_settings = {
                    "master_volume": 50,
                    "sfx_volume": 50,
                    "high_contrast": False,
                    "screen_reader": False,
                    "bible_version": "NIV",
                    "background_music": "Turn Your Eyes Upon Jesus.mp3"
                }
            
            # ✅ Use default settings if no user is logged in
            master_volume = current_app.user_settings.get("master_volume", 50) / 100  # Convert 0-100 to 0.0-1.0
            sfx_volume = current_app.user_settings.get("sfx_volume", 50) / 100
            
            # ✅ Delay setting volume to avoid crashes
            Clock.schedule_once(lambda _dt: self.adjust_volume(master_volume), 0.5)
            Clock.schedule_once(lambda _dt: self.adjust_volume(sfx_volume), 0.5)
            
            self.player.set_pause(False)
            # debug_print("Playback started")
            
            Clock.unschedule(self.check_player_state)
            Clock.schedule_interval(self.check_player_state, 1.0)
        
        except Exception as e:
            debug_print(f"Error in play_music (reset={reset}): {e}")
            self.player = None
    
    def adjust_volume(self, volume):
        """Adjusts the music volume after MediaPlayer has fully initialized."""
        if self.player:
            try:
                self.player.set_volume(volume)
                debug_print(f"Volume adjusted to {volume}")
            except Exception as e:
                debug_print(f"Error setting volume: {e}")
    
    # noinspection PyUnusedLocal
    def stop_music(self, dt=None):
        if self.player:
            self.player.set_pause(True)
        debug_print("Home screen music paused")
    
    # noinspection PyUnusedLocal
    def check_player_state(self, dt):
        if not self.player:
            return
        
        elapsed_time = self.player.get_pts()  # Get the current playback timestamp
        total_duration = self.player.get_metadata().get("duration", 0)  # Get the total audio file duration
        # debug_print(f"Elapsed time on music: {elapsed_time} / {total_duration}")
        
        if elapsed_time is None or elapsed_time == 0.0:
            debug_print("Music is stuck or stopped, restarting...")
            self.play_music(dt, reset=True, music_file=App.get_running_app().user_settings['background_music'])
        elif total_duration and elapsed_time >= total_duration - 0.5:
            debug_print("Music reached the end, restarting...")
            self.play_music(dt, reset=True, music_file=App.get_running_app().user_settings['background_music'])
    
    def update_button_box(self):
        debug_print("Updating button box.")
        if self.button_box in self.layout.children:
            self.layout.remove_widget(self.button_box)
        
        user_id = App.get_running_app().user_id
        conn, cursor = get_db_connection()
        
        try:
            cursor.execute("USE bible_trivia;")
            cursor.execute("""
                SELECT COUNT(*) FROM user_progress WHERE user_id = %s AND time_remaining > 0
            """, (user_id,))
            has_progress = cursor.fetchone()[0] > 0

            BUTTON_HEIGHT = 120
            BUTTON_SPACING = 20
            add_resume_button = has_progress and self.quiz_manager.game_over and self.has_left_game_this_session
            box_height = (BUTTON_HEIGHT * (4 if add_resume_button else 3)) + (BUTTON_SPACING * ((4 if add_resume_button else 3) - 1))
        
            # Expand button layout if resume button is to be added
            self.button_box = BoxLayout(
                orientation="vertical",
                spacing=20,
                size_hint_x=0.3,
                size_hint_y=None, # Original size when no resume button
                height=box_height,
                pos_hint={"x": 0.7, "center_y": 0.5}
            )
            
            play_button = Button(size_hint_y=None, size_hint_x=1, height=BUTTON_HEIGHT, 
                                 background_color=(1, 1, 1, 1),
                                 background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "PlayButton.png"),
                                 background_down=os.path.join(TEMP_ASSETS_DIR, "images", "PlayButtonPressed.png"),
                                 border=(0, 0, 0, 0)
                                 )
            play_button.bind(on_release=self.confirm_restart)
            self.button_box.add_widget(play_button)
            
            debug_print(f"Has progress: {has_progress}, Game over: {self.quiz_manager.game_over}, Left the game: {self.has_left_game_this_session}")

            # Add the resume button if there's progress
            if add_resume_button:  # One of these conditions isn't being met when it should
                debug_print("Adding resume button")
                resume_button = Button(size_hint_y=None, size_hint_x=1, height=BUTTON_HEIGHT, opacity=100,
                                       background_color=(1, 1, 1, 1),
                                       background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "ResumeButton.png"),
                                       background_down=os.path.join(TEMP_ASSETS_DIR, "images", "ResumeButtonPressed.png"),
                                       border=(0, 0, 0, 0)
                                       )
                resume_button.bind(on_release=self.resume_game)
                self.button_box.add_widget(resume_button)
            else:
                debug_print("No progress detected, skipping resume button.")
            
            options_button = Button(size_hint_y=None, size_hint_x=1, height=BUTTON_HEIGHT, opacity=100,
                                    background_color=(1, 1, 1, 1),
                                    background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "OptionsButton.png"),
                                    background_down=os.path.join(TEMP_ASSETS_DIR, "images", "OptionsButtonPressed.png"),
                                    border=(0, 0, 0, 0)
                                    )
            options_button.bind(on_release=self.open_options)
            self.button_box.add_widget(options_button)
            
            credits_button = Button(size_hint_y=None, size_hint_x=1, height=BUTTON_HEIGHT, opacity=100,
                                    background_color=(1, 1, 1, 1),
                                    background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "CreditsButton.png"),
                                    background_down=os.path.join(TEMP_ASSETS_DIR, "images", "CreditsButtonPressed.png"),
                                    border=(0, 0, 0, 0)
                                    )
            credits_button.bind(on_release=self.open_credits)
            self.button_box.add_widget(credits_button)
            
            self.layout.add_widget(self.button_box, index=2)
            debug_print("Button box updated")
    
        except mysql.connector.Error as e:
            debug_print(f"Database error in update_button_box: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # noinspection PyUnusedLocal
    def confirm_restart(self, instance):
        play_sfx("button_press_1.mp3")
        user_id = App.get_running_app().user_id
        conn, cursor = get_db_connection()
        
        try:
            cursor.execute("USE bible_trivia;")
            cursor.execute("""
                            SELECT COUNT(*) FROM user_progress WHERE user_id = %s AND time_remaining > 0
                        """, (user_id,))
            has_progress = cursor.fetchone()[0] > 0
            
            # If there is progress
            if has_progress:
                debug_print("Progress exists")
                content = BoxLayout(orientation="vertical")
                content.add_widget(Label(
                    text="Unresolved game found. Continue?"
                ))
                vbox = BoxLayout(orientation="vertical", size_hint_y=1)
                vbox.add_widget(Widget(size_hint_y=1))
                button_box = BoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height=180)
                button_box.add_widget(Widget(size_hint_x=1))
                button_box.add_widget(Button(
                    size_hint=(None, None), size=(320, 180),
                    background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "NewGameButton.png"), 
                    background_down=os.path.join(TEMP_ASSETS_DIR, "images", "NewGameButtonPressed.png"),
                    border=(0, 0, 0, 0),
                    on_release=lambda btn: (popup.dismiss(), self.new_game(btn))
                ))
                button_box.add_widget(Button(
                    size_hint=(None, None), size=(320, 180),
                    background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "ResumeGameButton.png"), 
                    background_down=os.path.join(TEMP_ASSETS_DIR, "images", "ResumeGameButtonPressed.png"),
                    border=(0, 0, 0, 0),
                    on_release=lambda btn: (popup.dismiss(), self.resume_game(btn))
                ))
                button_box.add_widget(Button(
                    size_hint=(None, None), size=(320, 180),
                    background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "CancelButton.png"), 
                    background_down=os.path.join(TEMP_ASSETS_DIR, "images", "CancelButtonPressed.png"),
                    border=(0, 0, 0, 0),
                    on_release=lambda btn: popup.dismiss()
                ))
                button_box.add_widget(Widget(size_hint_x=1))

                vbox.add_widget(button_box)
                vbox.add_widget(Widget(size_hint_y=1))

                content.add_widget(vbox)

                popup = Popup(title="", content=content, size_hint=(0.6, 0.27))
                popup.open()  # Prompt the user with the decision to start a new game or resume the previous one
            else:
                debug_print("There is no progress")
                self.quiz_screen.reset(None)  # Reset the state of the quiz screen
                self.manager.transition = FadeTransition()
                self.manager.current = "QuizOne"  # If there's no progress, then just switch to the quiz screen.
        
        except mysql.connector.Error as e:
            debug_print(f"Database error in confirm_restart: {e}")
        
        finally:
            cursor.close()
            conn.close()
    
    # noinspection PyUnusedLocal
    def resume_game(self, instance, *args):
        play_sfx("button_press_1.mp3")
        user_id = App.get_running_app().user_id
        debug_print(f"Attempting to resume game for user_id: {user_id}")
        conn, cursor = get_db_connection(dictionary=True)
        
        try:
            cursor.execute("USE bible_trivia;")
            cursor.execute("""
                SELECT current_bank_index, current_question, score, lives, time_remaining, last_question
                FROM user_progress WHERE user_id = %s
            """, (user_id,))
            progress = cursor.fetchone()
            debug_print(f"Fetched progress: {progress}")
            
            if progress:
                self.quiz_manager.load_progress()
                debug_print("Progress loaded successfully")
                self.manager.transition = FadeTransition()
                self.manager.current = "QuizOne"
                self.quiz_screen.start_quiz(None)
            else:
                print("No progress found; unable to resume game.")
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # noinspection PyUnusedLocal
    def new_game(self, instance, *args):
        play_sfx("button_press_1.mp3")
        self.quiz_screen.reset(True)
        debug_print("Quiz screen has been reset for a new game")
        self.quiz_screen.quiz_state = {}
        self.manager.transition = FadeTransition()
        self.manager.current = "QuizOne"
    
    # noinspection PyUnusedLocal
    def logout(self, instance):
        play_sfx("button_press_1.mp3")
        debug_print("Logging out user...")
        App.get_running_app().user_id = None  # Clear the session

        # Hide the username label
        self.username_label.text = ""
        self.username_label.opacity = 0
        self.username_label.size_hint = (None, None)
        self.username_label.size = (0, 0)
        self.username_label.pos_hint = {"center_x": -1, "top": 0.97}
        
        # Hide the logout button
        self.logout_button.opacity = 0
        self.logout_button.disabled = True
        self.logout_button.size_hint = (None, None)
        self.logout_button.size = (0, 0)
        self.logout_button.pos_hint = {"center_x": -1, "top": 0.9}
        
        # Show the login button
        self.login_button.opacity = 100
        self.login_button.disabled = False
    
    # noinspection PyUnusedLocal
    def start_game(self, instance):
        self.manager.transition = FadeTransition()
        self.manager.current = "QuizOne"
    
    # noinspection PyUnusedLocal
    def open_options(self, instance):
        play_sfx("button_press_1.mp3")
        self.manager.transition = FadeTransition()
        self.manager.current = "OptionsScreen"
    
    # noinspection PyUnusedLocal
    def open_credits(self, instance):
        play_sfx("button_press_1.mp3")
        self.manager.transition = FadeTransition()
        self.manager.current = "CreditsScreen"
    
    # noinspection PyUnusedLocal
    def open_login(self, instance):
        play_sfx("button_press_1.mp3")
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = "LoginScreen"

