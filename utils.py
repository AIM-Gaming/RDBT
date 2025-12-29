import pygame
import os
import sys
import json
import requests
from argon2 import PasswordHasher
from typing import Optional, Dict
from kivy.app import App

from db import get_db_connection
from log import debug_print


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and production. """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


LOCAL_USER_FILE = resource_path("last_logged_in.json")
ASSETS_ZIP_PATH = resource_path("assets/assets.zip")
TEMP_ASSETS_DIR = resource_path("temp_assets")
INACTIVIY_THRESHOLD = 60 * 5
API_BASE_URL = "http://127.0.0.1:8000"
ph = PasswordHasher()


def play_sound(file_path):
    """Plays a sound file using pygame."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.quit()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)  # Initialize the mixer
            # debug_print(f"Pygame mixer reinitialized: {pygame.mixer.get_init()}")
        
        sound = pygame.mixer.Sound(file_path)  # Load the sound file
        current_app = App.get_running_app()
        sfx_volume = current_app.user_settings["sfx_volume"] / 100  # Normalize volume to 0.0 - 1.0
        sound.set_volume(sfx_volume)  # Set the sound effect volume
        sound.play()  # Play the sound
        # debug_print(f"Playing sound from '{file_path}' with volume {sfx_volume}")
    
    except pygame.error as e:
        debug_print(f"Pygame error while playing sound: {e}")
    except Exception as e:
        print(f"Error while playing sound: {e}")

def play_sfx(file_name):
    # Construct the full path to the sound file
    file_path = os.path.join(TEMP_ASSETS_DIR, "sounds", file_name)

    # Play the sound
    play_sound(file_path)


def wrap_text(text, width=20, separator="\n"):
    """ Wrap text to insert newlines after every `width` character."""
    if not isinstance(text, str):
        text = str(text)
    
    lines = []
    current_line = ""
    
    for word in text.split():
        # Check if adding the word would exceed the width
        if len(current_line) + len(word) + 1 <= width:
            # Add word to the current line
            current_line += (word + " ")
        else:
            # Append current line and start a new one
            lines.append(current_line.strip().center(width))
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip().center(width))
    return separator.join(lines)

def save_last_logged_in(user_id, username):
    """Save the last logged-in user locally on the device"""
    with open(LOCAL_USER_FILE, "w") as file:
        json.dump({"user_id": user_id, "username": username}, file)


def last_logged_in():
    """Retrieve the last logged-in user locally from the device"""
    if os.path.exists(LOCAL_USER_FILE):
        with open(LOCAL_USER_FILE, "r") as file:
            return json.load(file)
    debug_print("No last logged-in user found")
    return None


def load_user_settings(user_id) -> Optional[Dict]:
    """ Fetches user settings from the database """
    response = requests.get(f"{API_BASE_URL}/users/{user_id}/settings")
    response.raise_for_status()
    if response.status_code == 200:
        settings = response.json()
        return settings
    else:
        debug_print(f"Failed to fetch user settings: {response.status_code}")
        return None


# noinspection PyUnusedLocal
def update_music_volume(instance, value):
    current_app = App.get_running_app()
    home_screen = current_app.manager.get_screen("HomeScreen")
    
    if home_screen.player:
        volume = value / 100
        home_screen.player.set_volume(volume)
        debug_print("Background music volume adjusted")


# noinspection PyUnusedLocal
def update_sfx_volume(instance, value):
    current_app = App.get_running_app()
    current_app.user_settings["sfx_volume"] = int(value)
    
    conn, cursor = get_db_connection()
    cursor.execute("USE users;")
    cursor.execute("UPDATE user_settings SET sfx_volume = %s WHERE user_id = %s", (int(value), current_app.user_id))
    conn.commit()
    
    cursor.close()
    conn.close()

