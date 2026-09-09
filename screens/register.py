from kivy.app import App
from kivy.uix.screenmanager import Screen, NoTransition, FadeTransition
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
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image

import os
import requests

from screens.login import login_user
from widgets.blurred_image import BlurredImage
from widgets.outlined_label import OutlinedLabel
from utils import debug_print, show_popup, TEMP_ASSETS_DIR, API_BASE_URL, ph


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()

        background_image = BlurredImage(source=os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(background_image)


        # CONSTANTS
        FIELD_WIDTH = 700
        FIELD_HEIGHT = 60
        FIELD_SPACING = 94
        box_height = FIELD_HEIGHT * 4 + FIELD_SPACING

        board_layout = FloatLayout(
            size_hint=(None, None),
            size=(1000, 750),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        register_board = Image(
            source=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterBoard.png"),
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
            allow_stretch=True, keep_ratio=False
        )

        input_box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=FIELD_WIDTH, height=box_height,
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            spacing=FIELD_SPACING
        )

        login_label = OutlinedLabel(text="Register for Bible Trivia", font_size=40, 
                                    pos_hint={"center_y": 0.99, "center_x": 0.5},
                                    outline_width=5, font_style=os.path.join(TEMP_ASSETS_DIR, "fonts", "Poppins-Black.ttf"))
        
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT, pos_hint={"center_y": 1.05})
        input_box.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(None, None), 
                                        width=FIELD_WIDTH, height=FIELD_HEIGHT, pos_hint={"center_y": 0.7})
        input_box.add_widget(self.password_input)

        self.confirm_password_input = TextInput(hint_text="Confirm Password", password=True, multiline=False, size_hint=(None, None), 
                                                width=FIELD_WIDTH, height=FIELD_HEIGHT, pos_hint={"center_y": 0.33})
        input_box.add_widget(self.confirm_password_input)

        self.first_name_input = TextInput(hint_text="First Name", multiline=False, size_hint=(None, None), 
                                          width=FIELD_WIDTH, height=FIELD_HEIGHT, pos_hint={"center_y": 0})
        input_box.add_widget(self.first_name_input)
        
        register_button = Button(size=(332.8, 187.2), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0},
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

        board_layout.add_widget(register_board)
        layout.add_widget(home_button)
        board_layout.add_widget(login_label)
        board_layout.add_widget(input_box)
        board_layout.add_widget(register_button)
        layout.add_widget(board_layout)
        layout.add_widget(login_button)
        
        self.add_widget(layout)
    
    # noinspection PyUnusedLocal
    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        confirm_pw = self.confirm_password_input.text
        first_name = self.first_name_input.text


        if not username.strip():
            show_popup("Stop tryna be anonymous", (0.4, 0.3), "Popup4-3.png")
            return
        if len(username.strip()) < 4:
            show_popup("Your username must be at least 4 characters long", (0.4, 0.2), "Popup4-2.png")
            return
        if not password:
            show_popup("Please enter a password for your account", (0.4, 0.2), "Popup4-2.png")
            return
        if len(password) < 8:
            show_popup("Your password must be at least 8 characters long", (0.4, 0.2), "Popup4-2.png")
            return
        if password != confirm_pw or not confirm_pw:
            show_popup("Make sure you use the same password to confirm", (0.4, 0.2), "Popup4-2.png")
            return
        if not first_name:
            show_popup("Enter your first name", (0.4, 0.3), "Popup4-3.png")
            return
        
        success = register_user(username, password, first_name)
        if success:
            user_id, settings = login_user(username, password)
            if user_id:
                App.get_running_app().user_id = user_id
                self.home_screen = self.manager.get_screen("HomeScreen")
                self.home_screen.logout_button.disabled = False
            show_popup("Registration successful!", (0.4, 0.3), "Popup4-3.png")
            username = ""
            password = ""
            self.manager.current = "HomeScreen"
        else:
            username = ""
            password = ""
    
    # noinspection PyUnusedLocal
    def open_login(self, instance):
        self.manager.transition = NoTransition()
        self.manager.current = "LoginScreen"
    
    # noinspection PyUnusedLocal
    def go_back(self, instance):
        self.manager.transition = FadeTransition()
        self.manager.current = "HomeScreen"
    
    def on_leave(self):
        self.username_input.text = ""
        self.password_input.text = ""

def register_user(username, password, first_name):
    result = False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/register_user", 
            json={
            "username": username,
            "pw_hash": ph.hash(password),
            "first_name": first_name
            }, timeout=10
        )
        if response.status_code == 409:
            show_popup("Username already exists", (0.4, 0.3), "Popup4-3.png")
            return False
        
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "success":
            show_popup(data.get("message", "Registration failed"), (0.4, 0.3), "Popup4-3.png")
            return False
        debug_print(f"User {username} registered successfully with user id: {data["user_id"]}")
        result = True
        return result

    except requests.Timeout:
        show_popup("The server took too long to respond", (0.4, 0.3), "Popup4-3.png")
    except requests.ConnectionError:
        show_popup("Could not connect to the server", (0.4, 0.3), "Popup4-3.png")
    except requests.HTTPError as e:
        debug_print(f"API error in register_user: {e}")
        show_popup("Reigstration failed. Please try again", (0.4, 0.3), "Popup4-3.png")
        return False