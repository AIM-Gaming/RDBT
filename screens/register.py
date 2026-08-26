from kivy.app import App
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

import os
import requests

from screens.login import login_user
from widgets.blurred_image import BlurredImage
from widgets.outlined_label import OutlinedLabel
from utils import debug_print, TEMP_ASSETS_DIR, API_BASE_URL


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()

        background_image = BlurredImage(source=os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(background_image)


        # CONSTANTS
        FIELD_WIDTH = 700
        FIELD_HEIGHT = 60
        FIELD_SPACING = 20
        box_height = FIELD_HEIGHT * 4 + FIELD_SPACING

        input_box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=FIELD_WIDTH, height=box_height,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=FIELD_SPACING
        )

        login_label = OutlinedLabel(text="Register for Bible Trivia", font_size=40, 
                                    pos_hint={"center_y": 0.75, "center_x": 0.5},
                                    outline_width=5)
        
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT)
        input_box.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT)
        input_box.add_widget(self.password_input)

        self.confirm_password_input = TextInput(hint_text="Confirm Password", password=True, multiline=False, size_hint=(None, None), 
                                                width=FIELD_WIDTH, height=FIELD_HEIGHT)
        input_box.add_widget(self.confirm_password_input)

        self.first_name_input = TextInput(hint_text="First Name", multiline=False, size_hint=(None, None), 
                                          width=FIELD_WIDTH, height=FIELD_HEIGHT)
        input_box.add_widget(self.first_name_input)
        
        register_button = Button(size=(332.8, 187.2), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.25},
                                 background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButton.png"),
                                 background_down=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButtonPressed.png"),
                                 border=(0, 0, 0, 0))
        register_button.bind(on_release=self.register)
        
        login_button = Button(size=(270, 118.5), size_hint=(None, None), pos_hint={"center_x": 0.9, "top": 0.95},
                                   background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButton.png"),
                                   background_down=os.path.join(TEMP_ASSETS_DIR, "images", "LoginButtonPressed.png"),
                                   border=(0, 0, 0, 0))
        login_button.bind(on_release=self.open_login)
        
        home_button = Button(size=(150, 150), size_hint=(None, None), pos_hint={"center_x": 0.05, "top": 0.95},
                             background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "BackButton.png"),
                             background_down=os.path.join(TEMP_ASSETS_DIR, "images", "BackButtonPressed.png"),
                             border=(0, 0, 0, 0))
        home_button.bind(on_release=self.go_back)
        layout.add_widget(home_button)
        
        layout.add_widget(login_label)
        layout.add_widget(input_box)
        layout.add_widget(register_button)
        layout.add_widget(login_button)
        
        self.add_widget(layout)
    
    # noinspection PyUnusedLocal
    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        confirm_pw = self.confirm_password_input.text
        first_name = self.first_name_input.text
        
        success = register_user(username, password, confirm_pw, first_name)
        if success:
            user_id, settings = login_user(username, password)
            if user_id:
                App.get_running_app().user_id = user_id
                self.home_screen = self.manager.get_screen("HomeScreen")
                self.home_screen.logout_button.disabled = False
            popup = Popup(title="", content=Label(text="Registration successful!"), size_hint=(0.4, 0.2))
            popup.open()
            username = ""
            password = ""
            self.manager.current = "HomeScreen"
        else:
            username = ""
            password = ""
            if password != confirm_pw:
                popup = Popup(title="", content=Label(text="Make sure you use the same password to confirm"),
                              size_hint=(0.4, 0.2))
            else:
                popup = Popup(title="", content=Label(text="Username already exists"), size_hint=(0.4, 0.2))
            popup.open()
    
    # noinspection PyUnusedLocal
    def open_login(self, instance):
        self.manager.transition = NoTransition()
        self.manager.current = "LoginScreen"
    
    # noinspection PyUnusedLocal
    def go_back(self, instance):
        self.manager.transition = NoTransition()
        self.manager.current = "HomeScreen"
    
    def on_leave(self):
        self.username_input.text = ""
        self.password_input.text = ""


def register_user(username, password, confirm_pw, first_name):
    result = False
    
    try:
        if password != confirm_pw:
            debug_print("Passwords have to match")
            return False
        
        response = requests.post(f"{API_BASE_URL}/register_user", json={
            "username": username,
            "password": password,
            "first_name": first_name
        })
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            debug_print(f"User {username} registered successfully with id {data["user_id"]}")
            result = True
            return result
        else:
            debug_print(f"User was unable to register successfully")
            return False
    
    except requests.HTTPError as e:
        debug_print(f"API error in register_user: {e}")
        return False