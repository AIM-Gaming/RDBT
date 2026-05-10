from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

import os

from widgets.clickable_label import ClickableLabel
from widgets.blurred_image import BlurredImage
from utils import TEMP_ASSETS_DIR, debug_print


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = FloatLayout()  # Float layout to hold everything
        self.add_widget(self.layout)

        self.background_texture = None
        self.texture_loaded = False

        self.bg_color = None
        self.bg_rect = None

        with self.layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            self.bg_color = Color(1, 1, 1, 1)  # White color
            self.bg_rect = Rectangle(pos=self.layout.pos, size=self.layout.size)
        
        self.layout.bind(pos=self.update_bg, size=self.update_bg)
        self.update_bg(None, None)
        
        # Define the scroll view (SV)
        self.scroll_view = ScrollView(size_hint=(0.8, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        # Content layout inside the scroll view
        self.content_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter("height"))  # Ensures proper scrolling
        self.scroll_view.add_widget(self.content_layout)  # Make content scrollable
        
        self.layout.add_widget(self.scroll_view)  # Add scroll view to the float layout
        
        self.add_credits_content()  # Add credits content

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
                    debug_print(f"CreditsScreen background texture loaded: {image_path}")
                else:
                    debug_print(f"CreditsScreen background image not found: {image_path}")
            except Exception as e:
                debug_print(f"Error loading CreditsScreen background texture: {e}")
    
    def add_credits_content(self):
        # Title
        title_label = Label(text="[b]Credits[/b]", markup=True, font_size=50, size_hint_y=None, height=50)
        self.content_layout.add_widget(title_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=50))
        
        # Development
        dev_label = Label(text="[b]Development[/b]", markup=True, font_size=35, size_hint_y=None, height=50)
        self.content_layout.add_widget(dev_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        dev_content = [
            {"name": "Soneal Pageot", "role": "Lead Developer"},
            {"name": "Genson Pageot", "role": "Lead Graphic Designer (supposedly)"}
        ]
        for dev in dev_content:
            developers = Label(text=f"{dev['name']} - {dev['role']}", markup=True, size_hint_y=None, font_size=30)
            self.content_layout.add_widget(developers)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))
        
        # Research
        research_label = Label(text="[b]Research[/b]", markup=True, font_size=35, size_hint_y=None, height=50)
        self.content_layout.add_widget(research_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        research_content = [
            {"name": "Soneal Pageot", "role": "Researcher"},
        ]
        for res in research_content:
            researchers = Label(text=f"{res['name']}", markup=True, size_hint_y=None, font_size=30)
            self.content_layout.add_widget(researchers)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))

        # Sound Design
        sound_label = Label(text="[b]Sound Design[/b]", markup=True, font_size=35, size_hint_y=None, height=50)
        self.content_layout.add_widget(sound_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        sound_content = [
            {"name": "Genson Pageot", "role": "SFX Design", "url": "https://linktr.ee/thecreatorpilot"},
            {"name": "TheLofiChristian", "role": "Music Design", "url": "https://www.lofichristian.com"},
        ]
        for sound in sound_content:
            if sound["url"]:
                sound_design = ClickableLabel(text=f"{sound['name']} | {sound['role']}", markup=True, size_hint_y=None, font_size=30, url=sound["url"])
            else:
                sound_design = Label(text=f"{sound['name']} | {sound['role']}", markup=True, size_hint_y=None, font_size=30)
            self.content_layout.add_widget(sound_design)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))
        
        # Special Thanks
        thanks_label = Label(text="[b]Special Thanks[/b]", markup=True, font_size=35, size_hint_y=None, height=50)
        self.content_layout.add_widget(thanks_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        thanks_content = [
            {"name": "Denaj Seymour"},
            {"name": "Esan Gilbert"},
            {"name": "Karrah Ferguson"},
            {"name": "Free Radicals"},
            {"name": "TheLofiChristian"},
            {"name": "The Father"},
            {"name": "The Son"},
            {"name": "The Holy Spirit"},
            {"name": "YOU"}
        ]
        for thx in thanks_content:
            mvp = Label(text=f"{thx['name']}", markup=True, size_hint_y=None, font_size=30)
            self.content_layout.add_widget(mvp)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))
        
        back_button = Button(size=(150, 150), size_hint=(None, None), pos_hint={"left": 1, "top": 1},
                             background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "BackButton.png"),
                             background_down=os.path.join(TEMP_ASSETS_DIR, "images", "BackButtonPressed.png"),
                             border=(0, 0, 0, 0))
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)
    
    # noinspection PyUnusedLocal
    def go_back(self, instance):
        self.manager.transition = NoTransition()
        self.manager.current = "HomeScreen"

