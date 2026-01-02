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
from utils import debug_print, TEMP_ASSETS_DIR, API_BASE_URL


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()

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

        login_label = Label(text="Register for Bible Trivia", font_size=40, pos_hint={"center_y": 0.75, "center_x": 0.5})
        
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
        
        register_button = Button(size=(360, 118.5), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.25},
                                 background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButton.png"),
                                 background_down=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButtonPressed.png"),
                                 border=(0, 0, 0, 0))
        register_button.bind(on_release=self.register)
        
        login_button = Button(size=(216, 94.6), size_hint=(None, None), pos_hint={"center_x": 0.9, "top": 0.95},
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
            popup = Popup(title="Success", content=Label(text="Registration successful!"), size_hint=(0.6, 0.3))
            popup.open()
            username = ""
            password = ""
            self.manager.current = "HomeScreen"
        else:
            username = ""
            password = ""
            if password != confirm_pw:
                popup = Popup(title="Error", content=Label(text="Make sure you use the same password to confirm"),
                              size_hint=(0.6, 0.3))
            else:
                popup = Popup(title="Error", content=Label(text="Username already exists"), size_hint=(0.6, 0.3))
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
        }).json()

        if response["status"] == "success":
            debug_print(f"User {username} registered successfully with id {response["user_id"]}")
            result = True
            return result
    
    except requests.HTTPError as e:
        debug_print(f"API error in register_user: {e}")
        return False
import os
import mysql.connector

from db import get_db_connection
from screens.login import login_user
from utils import debug_print, TEMP_ASSETS_DIR, ph


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = FloatLayout()

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

        login_label = Label(text="Register for Bible Trivia", font_size=40, pos_hint={"center_y": 0.75, "center_x": 0.5})
        
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
        
        register_button = Button(size=(360, 118.5), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.25},
                                 background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButton.png"),
                                 background_down=os.path.join(TEMP_ASSETS_DIR, "images", "RegisterButtonPressed.png"),
                                 border=(0, 0, 0, 0))
        register_button.bind(on_release=self.register)
        
        login_button = Button(size=(216, 94.6), size_hint=(None, None), pos_hint={"center_x": 0.9, "top": 0.95},
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
            popup = Popup(title="Success", content=Label(text="Registration successful!"), size_hint=(0.6, 0.3))
            popup.open()
            username = ""
            password = ""
            self.manager.current = "HomeScreen"
        else:
            username = ""
            password = ""
            if password != confirm_pw:
                popup = Popup(title="Error", content=Label(text="Make sure you use the same password to confirm"),
                              size_hint=(0.6, 0.3))
            else:
                popup = Popup(title="Error", content=Label(text="Username already exists"), size_hint=(0.6, 0.3))
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
    conn, cursor = get_db_connection()
    password_hash = ph.hash(password)
    result = False
    
    try:
        if password != confirm_pw:
            debug_print("Passwords have to match")
            return False
        
        cursor.execute("USE users;")
        
        # Check if the username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            debug_print("Username already exists in the database")
            return False
        
        # Insert the new user into the database
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name) VALUES (%s, %s, %s)
        """, (username, password_hash, first_name))
        conn.commit()
        
        # Get the user's id (to insert default data)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        
        # Insert default settings
        cursor.execute("""
            INSERT INTO user_settings (user_id, master_volume, sfx_volume, high_contrast, bible_version)
            VALUES (%s, 50, 50, FALSE, 'NIV')
        """, (user_id,))
        conn.commit()
        
        # Set default high score
        cursor.execute("""
            INSERT INTO user_score (user_id, high_score) VALUES (%s, 0)
        """, (user_id,))
        conn.commit()
        
        debug_print(f"User {username} registered successfully with id {user_id}")
        result = True
    
    except mysql.connector.Error as e:
        debug_print(f"Database error in register_user: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()
        return result


def register_user(username, password, confirm_pw, first_name):
    conn, cursor = get_db_connection()
    password_hash = ph.hash(password)
    result = False
    
    try:
        if password != confirm_pw:
            debug_print("Passwords have to match")
            return False
        
        cursor.execute("USE users;")
        
        # Check if the username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            debug_print("Username already exists in the database")
            return False
        
        # Insert the new user into the database
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name) VALUES (%s, %s, %s)
        """, (username, password_hash, first_name))
        conn.commit()
        
        # Get the user's id (to insert default data)
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        
        # Insert default settings
        cursor.execute("""
            INSERT INTO user_settings (user_id, master_volume, sfx_volume, high_contrast, bible_version)
            VALUES (%s, 50, 50, FALSE, 'NIV')
        """, (user_id,))
        conn.commit()
        
        # Set default high score
        cursor.execute("""
            INSERT INTO user_score (user_id, high_score) VALUES (%s, 0)
        """, (user_id,))
        conn.commit()
        
        debug_print(f"User {username} registered successfully with id {user_id}")
        result = True
    
    except mysql.connector.Error as e:
        debug_print(f"Database error in register_user: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()
        return result