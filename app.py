from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label

import os
import shutil
import requests
import mysql.connector
from datetime import datetime
from kivy.core.window import Window

from utils import debug_print, last_logged_in, load_user_settings, TEMP_ASSETS_DIR, INACTIVIY_THRESHOLD
from db import get_db_connection
from screens.intro import IntroScreen
from screens.home import HomeScreen
from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.quiz1 import QuizOne
from screens.options import OptionsScreen
from screens.credits import CreditsScreen


class BibleTriviaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.version = "0.1.0 Alpha"

        self.manager = None
        self.user_id = None
        self.inactivity_check_event = None
        self.last_activity_update_time = None
        self.activity_update_cooldown = 5  # Only update every 5 seconds max to avoid spam
        self.user_settings = {
            "master_volume": 50,
            "sfx_volume": 50,
            "high_contrast": False,
            "bible_versions": 'NIV',
            "background_music": 'Turn Your Eyes Upon Jesus.mp3'
        }
        self.high_score = None
        
        # Question banks and state variables
        self.current_bank_index = 1
        self.game_over = True
    
    def build(self):
        # Bind user input events to update last activity
        Window.bind(on_motion=self.on_user_activity)
        Window.bind(on_keyboard=self.on_user_activity)
        Window.bind(on_touch_down=self.on_user_activity)
        
        # Check for inactivity every 60 seconds
        self.inactivity_check_event = Clock.schedule_interval(self.check_inactivity, 60)
        self.manager = ScreenManager()
        
        # Add screens (frames) to the ScreenManager
        self.manager.add_widget(IntroScreen(name="IntroScreen"))
        self.manager.add_widget(HomeScreen(name="HomeScreen"))
        self.manager.add_widget(LoginScreen(name="LoginScreen"))
        self.manager.add_widget(RegisterScreen(name="RegisterScreen"))
        self.manager.add_widget(QuizOne(name="QuizOne"))
        self.manager.add_widget(OptionsScreen(name="OptionsScreen"))
        self.manager.add_widget(CreditsScreen(name="CreditsScreen"))
        
        # Auto log-in the last user
        last_user = last_logged_in()
        if last_user:
            self.user_id = last_user.get("user_id")
            settings = load_user_settings(self.user_id)
            if settings:
                self.user_settings = settings
                # Update last_active immediately after login
                self.update_last_active(0)
        
        if self.user_settings["high_contrast"]:
            self.apply_high_contrast(True)
        
        # Show the initial screen
        self.show_screen("IntroScreen")
        return self.manager

    def on_start(self):
        if not self.user_id:
            return
        response = requests.post(f"{API_BASE_URL}/users/{self.user_id}/set_last_active")
        response.raise_for_status()
    
    def on_pause(self):
        """Triggered when app is paused (e.g. minimized)"""
        screen = self.get_running_screen()
        if hasattr(self, "save_progress"):
            screen.save_progress()
        return True
    
    def on_stop(self):
        """Triggered when app is about to close"""
        screen = self.get_running_screen()
        if hasattr(self, "save_progress"):
            screen.save_progress()
        
        # Log out the user
        if self.user_id:
            conn, cursor = get_db_connection()
            try:
                cursor.execute("USE users;")
                cursor.execute("UPDATE users SET logged_in = FALSE WHERE id = %s", (self.user_id,))
                conn.commit()
            except mysql.connector.Error as e:
                debug_print(f"Database error during logout: {e}")
            finally:
                cursor.close()
                conn.close()
            self.user_id = None
        
        # Stop the inactivity check event
        if self.inactivity_check_event:
            Clock.unschedule(self.inactivity_check_event)
        
        # --- Ensure all media players are closed before deletion ---
        try:
            home_screen = self.manager.get_screen("HomeScreen")
            if hasattr(home_screen, "player") and home_screen.player:
                home_screen.player.set_pause(True)
                home_screen.player.close_player()
                home_screen.player = None
        except Exception as e:
            debug_print(f"Error closing HomeScreen player: {e}")
        
        try:
            intro_screen = self.manager.get_screen("IntroScreen")
            if hasattr(intro_screen, "player") and intro_screen.player:
                intro_screen.player.close_player()
                intro_screen.player = None
        except Exception as e:
            debug_print(f"Error closing IntroScreen player: {e}")
        
        # Clean up temporary songs directory
        if os.path.exists(TEMP_ASSETS_DIR):
            shutil.rmtree(TEMP_ASSETS_DIR)
            debug_print(f"Temporary assets directory {TEMP_ASSETS_DIR} deleted")
    
    def update_last_active(self, dt):
        """Updates the last active timestamp for the logged-in user."""
        if self.user_id:
            conn, cursor = get_db_connection()
            try:
                cursor.execute("USE users;")
                cursor.execute("UPDATE users SET last_active = NOW() WHERE id = %s", (self.user_id,))
                conn.commit()
            except mysql.connector.Error as e:
                debug_print(f"Database error during heartbeat: {e}")
            finally:
                cursor.close()
                conn.close()
    
    def on_user_activity(self, window, *args):
        """Called on mouse motion, keyboard, or touch events."""
        # If no user is logged in, do NOT consume the event - return False so widgets still receive input.
        if not self.user_id:
            return False
        
        # Throttle updates to avoid API spam (max once every 5 seconds)
        now = datetime.now().timestamp()
        if self.last_activity_update_time is None or (now - self.last_activity_update_time) >= self.activity_update_cooldown:
            self.last_activity_update_time = now
            self.update_last_active(0)
        
        return False
    
    def check_inactivity(self, dt):
        """Check if the user has been inactive for too long and logs them out"""
        debug_print("check_inactivity() accessed")
        if self.user_id:
            conn, cursor = get_db_connection(dictionary=True)
            try:
                cursor.execute("USE users;")
                cursor.execute("SELECT last_active FROM users WHERE id = %s", (self.user_id,))
                result = cursor.fetchone()

                if result and result.get("last_active"):
                    last_active = datetime.fromisoformat(result["last_active"])
                    now = datetime.now()

                    # Check if the user has been inactive for too long
                    if (now - last_active).total_seconds() > INACTIVIY_THRESHOLD:
                        debug_print(f"User {self.user_id} has been inactive for too long. Logging out...")
                        self.logout_user()
            
            except mysql.connector.Error as e:
                debug_print(f"Database error during inactivity check: {e}")
            finally:
                cursor.close()
                conn.close()
    
    def get_running_screen(self):
        try:
            return self.root.current_screen
        except AttributeError:
            return None
    
    def logout_user(self):
        """Logs out the current user"""
        debug_print("Logging out user (app.py)")
        if self.user_id:
            conn, cursor = get_db_connection()
            try:
                cursor.execute("USE users;")
                cursor.execute("UPDATE users SET logged_in = FALSE WHERE id = %s", (self.user_id,))
                conn.commit()
            except mysql.connector.Error as e:
                debug_print(f"Database error during logout: {e}")
            finally:
                cursor.close()
                conn.close()
            self.user_id = None
            self.last_activity_update_time = None
        
        # Refresh the home screen UI to reflect logged-out state
        try:
            if self.manager.current == "HomeScreen":
                home_screen = self.manager.get_screen("HomeScreen")
                home_screen.on_enter()
        except Exception as e:
            debug_print(f"Error refreshing home screen after logout: {e}")
    
    def show_screen(self, screen_name):
        self.manager.current = screen_name  # Use this format to switch screens
    
    def apply_high_contrast(self, enable: bool):
        """Apply high contrast mode to the app."""
        if enable:
            # Define high contrast colors
            # These colors are just examples; you can adjust them as needed
            high_contrast_bg = [0, 0, 0, 1]  # Black background
            high_contrast_text = [1, 1, 1, 1]  # White text
            high_contrast_button = [1, 1, 0, 1]  # Yellow button

            # Apply high contrast settings to all screens
            for screen in self.manager.screens:
                if hasattr(screen, "layout"):
                    screen.layout.canvas.before.clear()
                    with screen.layout.canvas.before:
                        Color(*high_contrast_bg)
                        Rectangle(size=screen.layout.size, pos=screen.layout.pos)

                # Update labels and buttons
                for widget in screen.walk():
                    if isinstance(widget, Label):
                        widget.color = high_contrast_text
                    elif isinstance(widget, Button):
                        widget.background_color = high_contrast_button
        
        else:
            # Reset to default colors (placeholder logic)
            for screen in self.manager.screens:
                if hasattr(screen, "layout"):
                    screen.layout.canvas.before.clear()