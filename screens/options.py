from kivy.app import App
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox

import os
import requests

from utils import debug_print, update_music_volume, update_sfx_volume, TEMP_ASSETS_DIR, API_BASE_URL
from widgets.carousel_selector import CarouselSelector
from widgets.blurred_image import BlurredImage


class OptionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        self.background_image = BlurredImage(source=os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png"), allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.background_image)

        self.scroll_image = Image(source=os.path.join(TEMP_ASSETS_DIR, "images", "OptionsScreenScroll.png"), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.layout.add_widget(self.scroll_image, index=0)

        self.papyrus_container = FloatLayout(size=(1000, 1100), size_hint=(None, None), pos_hint={"center_x": 0.5, "center_y": 0.5})        
        
        self.scroll_view = ScrollView(size_hint=(0.9, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.papyrus_container.add_widget(self.scroll_view)
        
        self.settings_layout = BoxLayout(orientation="vertical", spacing=20, size_hint_y=None, padding=[20, 20])
        self.settings_layout.bind(minimum_height=self.settings_layout.setter("height"))

        self.scroll_view.add_widget(self.settings_layout)
        self.layout.add_widget(self.papyrus_container)
        
        # Widgets
        self.master_volume = None
        self.sfx_volume = None
        self.bible_versions = None
        self.music_files = None
        self.music_selector = None
        self.high_contrast = None
        self.save_button = None
        
        self.add_options_content()

    def update_bg(self, instance, value):
        """Forces the background to fill the whole screen"""
        if getattr(self, 'background_texture', None):
            self.bg_rect.texture = self.background_texture
        self.bg_rect.size = self.layout.size
        self.bg_rect.pos = self.layout.pos
    
    def on_pre_enter(self, *args):
        """Load background texture before screen is displayed"""
        if not self.texture_loaded:
            try:
                image_path = os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png")
                if os.path.exists(image_path):
                    self.blurred_bg_obj = BlurredImage(image_path)
                    self.background_texture = self.blurred_bg_obj.texture
                    
                    self.bg_rect.texture = self.background_texture
                    self.bg_rect.size = self.layout.size
                    self.bg_rect.pos = self.layout.pos
                    
                    self.layout.canvas.ask_update()
                    self.texture_loaded = True
                    debug_print(f"OptionsScreen background texture loaded: {image_path}")
                else:
                    debug_print(f"OptionsScreen background image not found: {image_path}")
            except Exception as e:
                debug_print(f"Error loading OptionsScreen background texture: {e}")
    
    def add_options_content(self):
        # Title
        title_label = Label(text="Options", markup=True, font_size=50, size_hint_y=None, height=50)
        self.settings_layout.add_widget(title_label)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        # Volume Settings
        volume_label = Label(text="Volume Settings", markup=True, font_size=30, size_hint_y=None, height=40)
        self.settings_layout.add_widget(volume_label)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        self.master_volume = Slider(min=0, max=100, value=50, size_hint_y=None, height=40, size_hint_x=0.4,
                                    pos_hint={"center_x": 0.5})
        self.master_volume.bind(value=update_music_volume)  # Update music volume
        self.settings_layout.add_widget(Label(text="Master Volume", size_hint_y=None, height=10))
        self.settings_layout.add_widget(self.master_volume)
        
        self.sfx_volume = Slider(min=0, max=100, value=App.get_running_app().user_settings["sfx_volume"],
                                 size_hint_y=None, height=40, size_hint_x=0.4, pos_hint={"center_x": 0.5})
        self.sfx_volume.bind(value=update_sfx_volume)
        self.settings_layout.add_widget(Label(text="SFX Volume", size_hint_y=None, height=10))
        self.settings_layout.add_widget(self.sfx_volume)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=50))
        
        # Bible Version
        bible_version_label = Label(text="Bible Version", markup=True, font_size=30, size_hint_y=None, height=40)
        self.settings_layout.add_widget(bible_version_label)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=10))
        
        self.bible_versions = Spinner(text="NIV", values=("NIV", "KJV", "ESV", "NKJV", "NLT"), size_hint_y=None,
                                      height=40, size_hint_x=0.2, pos_hint={"center_x": 0.5})
        self.settings_layout.add_widget(self.bible_versions)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=50))

        # Background music
        music_label = Label(text="Background Music", markup=True, font_size=30, size_hint_y=None, height=40)
        self.settings_layout.add_widget(music_label)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=10))

        # Store all music files in assets.zip
        self.music_files = []
        for file in os.listdir(os.path.join(TEMP_ASSETS_DIR, "music")):
            if file.endswith(".mp3"):
                self.music_files.append(file)

        # Music selector
        self.music_selector = CarouselSelector(
            items=self.music_files,
            size_hint_y=None, 
            height=40, size_hint_x=0.4, pos_hint={"center_x": 0.5}
            )
        self.music_selector.bind(selected_item=self.play_demo_music)
        self.settings_layout.add_widget(self.music_selector)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=50))
        
        
        # Accessibility Options
        accessibility_label = Label(text="Accessibility Options", markup=True, font_size=30, size_hint_y=
        None, height=40)
        self.settings_layout.add_widget(accessibility_label)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=10))
        
        self.high_contrast = CheckBox(size_hint_y=None, height=40)
        self.high_contrast.active = App.get_running_app().user_settings["high_contrast"]
        self.high_contrast.bind(active=self.toggle_high_contrast)
        self.settings_layout.add_widget(Label(text="High Contrast Mode", size_hint_y=None, height=40))
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.settings_layout.add_widget(self.high_contrast)
        self.settings_layout.add_widget(Widget(size_hint_y=None, height=50))
        
        # Save Button
        self.save_button = Button(size_hint=(None, None), 
                                  size=(200, 100), border=(0, 0, 0, 0),
                                  pos_hint={"center_x": 0.5, "y": 0.07},
                                  background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "SaveButton.png"),
                                  background_down=os.path.join(TEMP_ASSETS_DIR, "images", "SaveButtonPressed.png"))
        self.save_button.bind(on_release=self.save_settings)
        self.papyrus_container.add_widget(self.save_button)
        self.layout.add_widget(Widget())
        
        back_button = Button(size=(150, 150), size_hint=(None, None), pos_hint={"left": 1, "top": 1},
                             background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "BackButton.png"),
                             background_down=os.path.join(TEMP_ASSETS_DIR, "images", "BackButtonPressed.png"),
                             border=(0, 0, 0, 0))
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)
    
    def toggle_high_contrast(self, instance, value):
        current_app = App.get_running_app()
        current_app.user_settings["high_contrast"] = value
        
        response = requests.post(f"{API_BASE_URL}/users/{current_app.user_id}/settings/update_high_contrast", json={"value": value})
        response.raise_for_status()
        
        debug_print(f"High contrast mode set to {value}")
    
    def play_demo_music(self, instance, value):
        home_screen = self.manager.get_screen("HomeScreen")
        if home_screen.player:
            try:
                home_screen.player.set_pause(True)
                home_screen.player.close_player()
                home_screen.player = None
            except Exception as e:
                debug_print(f"Error stopping music: {e}")

        if value:
            try:
                debug_print(f"Switching music to {value}")
                Clock.schedule_once(lambda dt: home_screen.play_music(reset=True, music_file=value), 0.2)
                debug_print(f"Playing demo music: {value}")
            except Exception as e:
                debug_print(f"Error playing demo music: {e}")
    
    # noinspection PyUnusedLocal
    def save_settings(self, instance=None):
        current_app = App.get_running_app()
        user_id = current_app.user_id
        
        new_master_volume = int(self.master_volume.value)
        new_sfx_volume = int(self.sfx_volume.value)
        new_bible_version = self.bible_versions.text
        new_high_contrast = self.high_contrast.active
        new_background_music = self.music_selector.selected_item
        
        new_settings = {
            "master_volume": new_master_volume,
            "sfx_volume": new_sfx_volume,
            "bible_version": new_bible_version,
            "high_contrast": new_high_contrast,
            "background_music": new_background_music
        }

        response = requests.post(f"{API_BASE_URL}/users/{user_id}/settings/save_settings", json=new_settings)
        response.raise_for_status()
        
        current_app.user_settings["master_volume"] = new_master_volume
        current_app.user_settings["sfx_volume"] = new_sfx_volume
        current_app.user_settings["bible_version"] = new_bible_version
        current_app.user_settings["high_contrast"] = new_high_contrast
        current_app.user_settings["background_music"] = new_background_music
        
        self.manager.current = "HomeScreen"
        debug_print("User settings successfully updated")
    
    # noinspection PyUnusedLocal
    def go_back(self, instance):
        self.manager.transition = NoTransition()
        self.manager.current = "HomeScreen"