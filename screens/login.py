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
import requests
from typing import Dict, Tuple, Optional

from widgets.blurred_image import BlurredImage
from widgets.outlined_label import OutlinedLabel
from utils import debug_print, save_last_logged_in, load_user_settings, TEMP_ASSETS_DIR, API_BASE_URL, ph
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()

        background_image = BlurredImage(source=os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(background_image)

        # CONSTANTS
        FIELD_WIDTH = 700
        FIELD_HEIGHT = 60
        FIELD_SPACING = 20
        box_height = FIELD_HEIGHT * 2 + FIELD_SPACING

        board_layout = FloatLayout(
            size_hint=(None, None),
            size=(1000, 500),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        with board_layout.canvas.before:
            Color(1, 0, 0, 1)
            rect = Rectangle(pos=board_layout.pos, size=board_layout.pos)
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        board_layout.bind(pos=update_rect, size=update_rect)

        # INPUT FIELDS (Middle Position)
        input_box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=FIELD_WIDTH, height=box_height,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=FIELD_SPACING
        )

        login_label = OutlinedLabel(text="Login to Bible Trivia", font_size=40, 
                                    pos_hint={"center_y": 0.8, "center_x": 0.5},
                                    outline_width=5)
        
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT)
        input_box.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT)
        input_box.add_widget(self.password_input)
        
        self.home_screen = None
        
        login_button = Button(size=(351, 154.05), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.15},
                              background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButton.png"),
                              background_down=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButtonPressed.png"),
                              border=(0, 0, 0, 0))
        login_button.bind(on_release=self.login)
        
        register_button = Button(size=(256, 144), size_hint=(None, None), pos_hint={"center_x": 0.9, "top": 0.95},
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
        board_layout.add_widget(login_label)
        board_layout.add_widget(input_box)
        board_layout.add_widget(login_button)
        layout.add_widget(board_layout)
        layout.add_widget(register_button)
        
        
        self.add_widget(layout)
    
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
            # Update last_active immediately after login
            App.get_running_app().update_last_active(0)
            self.manager.current = "HomeScreen"
        else:
            username = ""
            password = ""
            popup = Popup(title="", content=Label(text="Invalid username or password"), size_hint=(0.4, 0.3))
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
    
    user_id: Optional[int] = None
    settings: Optional[Dict] = None
    
    try:
        response = requests.get(f"{API_BASE_URL}/login_user", json={"username": username})
        response.raise_for_status()
        user = response.json()
        
        if user:
            user_id, stored_hash, logged_in = user
            if logged_in:
                debug_print(f"User {username} is already logged in on another device")
                return None, None  # Deny login if already logged in elsewhere
            try:
                ph.verify(stored_hash, password)
                update_request = requests.post(f"{API_BASE_URL}/users/{user_id}/set_last_logged_in")
                update_request.raise_for_status()

                # Save locally
                save_last_logged_in(user_id, username)
                
                debug_print(f"Login successful for user {username}!")
                settings = load_user_settings(user_id) or {
                    "master_volume": 50,
                    "sfx_volume": 50,
                    "high_contrast": False,
                    "bible_version": "NIV"
                }
            
                # Ensure inactivity checker is scheduled
                app = App.get_running_app()
                try:
                    if getattr(app, "inactivity_check_event", None):
                        Clock.unschedule(app.inactivity_check_event)
                except Exception:
                    pass
                app.inactivity_check_event = Clock.schedule_interval(app.check_inactivity, 60)

            except Exception as e:
                debug_print(f"Incorrect password for user {username}: {e}")
                user_id = None
                settings = None
        else:
            debug_print("Username not found in database")
    
    except requests.HTTPError as e:
        debug_print(f"API error in login_user: {e}")
        user_id = None
        settings = None
    
    return user_id, settings