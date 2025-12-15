from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
# from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

import os
from typing import Dict, Tuple, Optional

from db import get_db_connection
from utils import debug_print, save_last_logged_in, load_user_settings, TEMP_ASSETS_DIR, ph

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()

        # CONSTANTS
        FIELD_WIDTH = 700
        FIELD_HEIGHT = 60
        FIELD_SPACING = 20
        box_height = FIELD_HEIGHT * 2 + FIELD_SPACING

        # INPUT FIELDS (Middle Position)
        input_box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=FIELD_WIDTH, height=box_height,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=FIELD_SPACING
        )

        self.login_label = Label(text="Login to Bible Trivia", font_size=40, pos_hint={"center_y": 0.75, "center_x": 0.5})
        
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT, pos_hint={"center_x": 0.5, "top": 1})
        input_box.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT, pos_hint={"center_x": 0.5, "bottom": 1})
        input_box.add_widget(self.password_input)
        
        self.home_screen = None
        
        login_button = Button(size=(270, 118.5), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.25},
                              background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButton.png"),
                              background_down=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButtonPressed.png"),
                              border=(0, 0, 0, 0))
        login_button.bind(on_release=self.login)
        
        register_button = Button(size=(288, 94.8), size_hint=(None, None), pos_hint={"center_x": 0.9, "top": 0.95},
                                 background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButton.png"),
                                 background_down=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButtonPressed.png"),
                                 border=(0, 0, 0, 0))
        register_button.bind(on_release=self.open_registration)
        
        home_button = Button(size=(150, 150), size_hint=(None, None), pos_hint={"center_x": 0.05, "top": 0.95},
                             background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "BackButton.png"),
                             background_down=os.path.join(TEMP_ASSETS_DIR, "images", "BackButtonPressed.png"),
                             border=(0, 0, 0, 0))
        home_button.bind(on_release=self.go_back)

        layout.add_widget(home_button)
        layout.add_widget(self.login_label)
        layout.add_widget(input_box)
        layout.add_widget(login_button)
        layout.add_widget(register_button)
        
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    # noinspection PyUnusedLocal
    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        user_id, settings = login_user(username, password)
        if user_id:
            App.get_running_app().user_id = user_id
            self.home_screen = self.manager.get_screen("HomeScreen")
            self.home_screen.logout_button.disabled = False
            username = ""
            password = ""
            self.manager.current = "HomeScreen"
        else:
            username = ""
            password = ""
            popup = Popup(title="Error", content=Label(text="Invalid username or password"), size_hint=(0.6, 0.3))
            popup.open()
    
    # noinspection PyUnusedLocal
    def open_registration(self, instance):
        self.manager.transition = NoTransition()
        self.manager.current = "RegisterScreen"
    
    # noinspection PyUnusedLocal
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "HomeScreen"
    
    def on_leave(self):
        self.username_input.text = ""
        self.password_input.text = ""

def login_user(username: str, password: str) -> Tuple[Optional[int], Optional[Dict]]:
    conn, cursor = get_db_connection()
    
    user_id: Optional[int] = None
    settings: Optional[Dict] = None
    
    try:
        cursor.execute("USE users;")
        cursor.execute("SELECT id, password_hash, logged_in FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            user_id, stored_hash, logged_in = user
            if logged_in:
                debug_print(f"User {username} is already logged in on another device")
                return None, None  # Deny login if already logged in elsewhere
            try:
                ph.verify(stored_hash, password)
                cursor.execute("UPDATE users SET last_logged_in = NOW() WHERE id = %s", (user_id,))
                conn.commit()

                # Save locally
                save_last_logged_in(user_id, username)
                
                debug_print(f"Login successful for user {username}!")
                settings = load_user_settings(user_id) or {
                    "master_volume": 50,
                    "sfx_volume": 50,
                    "high_contrast": False,
                    "bible_version": "NIV"
                }
            
                # Restart the heartbeat event
                app = App.get_running_app()
                if app.heartbeat_event:
                    Clock.unschedule(app.heartbeat_event)
                app.heartbeat_Event = Clock.schedule_interval(app.update_last_active, 60)

            except Exception as e:
                debug_print(f"Incorrect password for user {username}: {e}")
                user_id = None
                settings = None
        else:
            debug_print("Username not found in database")
    
    except Exception as e:
        debug_print(f"Database error in login_user: {e}")
        user_id = None
        settings = None
    
    finally:
        cursor.close()
        conn.close()
    
    return user_id, settings

