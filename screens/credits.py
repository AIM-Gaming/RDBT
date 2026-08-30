from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image

import os

from widgets.clickable_label import ClickableLabel
from widgets.blurred_image import BlurredImage
from widgets.outlined_label import OutlinedLabel
from utils import TEMP_ASSETS_DIR, wrap_text, debug_print


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = FloatLayout()  # Float layout to hold everything
        self.add_widget(self.layout)

        self.background_image = BlurredImage(source=os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png"), allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.background_image)

        self.scroll_image = Image(source=os.path.join(TEMP_ASSETS_DIR, "images", "PapyrusScroll.png"), pos_hint={"center_x": 0.49, "center_y": 0.5})
        self.layout.add_widget(self.scroll_image, index=0)
        
        # Define the scroll view (SV)
        self.scroll_view = ScrollView(size_hint=(0.8, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        # Content layout inside the scroll view
        self.content_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter("height"))  # Ensures proper scrolling
        self.scroll_view.add_widget(self.content_layout)  # Make content scrollable
        
        self.layout.add_widget(self.scroll_view)  # Add scroll view to the float layout
        
        self.add_credits_content()  # Add credits content
    
    def add_credits_content(self):
        # Title
        title_label = OutlinedLabel(text="Credits", markup=True, font_size=50, size_hint_y=None, height=50, outline_width=3)
        self.content_layout.add_widget(title_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=50))
        
        # Development
        dev_label = OutlinedLabel(text="Development", markup=True, font_size=35, size_hint_y=None, height=50, outline_width=3)
        self.content_layout.add_widget(dev_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        dev_content = [
            {"name": "Soneal Pageot", "role": "Lead Developer"},
            {"name": "Genson Pageot", "role": "Lead Graphic Designer (supposedly)"}
        ]
        for dev in dev_content:
            developers = OutlinedLabel(text=wrap_text(text=wrap_text(f"{dev['name']} - {dev['role']}", width=25)), markup=True, size_hint_y=None, font_size=30, outline_width=2)
            self.content_layout.add_widget(developers)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))
        
        # Research
        research_label = OutlinedLabel(text=wrap_text(text="Research"), markup=True, font_size=35, size_hint_y=None, height=50, outline_width=3)
        self.content_layout.add_widget(research_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        research_content = [
            {"name": "Soneal Pageot", "role": "Researcher"},
        ]
        for res in research_content:
            researchers = OutlinedLabel(text=wrap_text(text=wrap_text(f"{res['name']}", width=25)), markup=True, size_hint_y=None, font_size=30, outline_width=2)
            self.content_layout.add_widget(researchers)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))

        # Sound Design
        sound_label = OutlinedLabel(text=wrap_text(text="Sound Design"), markup=True, font_size=35, size_hint_y=None, height=50, outline_width=3)
        self.content_layout.add_widget(sound_label)
        self.content_layout.add_widget(Widget(size_hint_y=None, height=20))
        
        sound_content = [
            {"name": "Genson Pageot", "role": "SFX Design", "url": "https://linktr.ee/thecreatorpilot"},
            {"name": "TheLofiChristian", "role": "Music Design", "url": "https://www.lofichristian.com"},
        ]
        for sound in sound_content:
            if sound["url"]:
                sound_design = ClickableLabel(text=wrap_text(f"{sound['name']} | {sound['role']}", width=25), markup=True, size_hint_y=None, font_size=30, url=sound["url"])
            else:
                sound_design = OutlinedLabel(text=f"{sound['name']} | {sound['role']}", markup=True, size_hint_y=None, font_size=30, outline_width=2)
            self.content_layout.add_widget(sound_design)
            self.content_layout.add_widget(Widget(size_hint_y=None, height=10))
        self.content_layout.add_widget(Widget(size_hint_y=None, height=40))
        
        # Special Thanks
        thanks_label = OutlinedLabel(text=wrap_text(text="Special Thanks"), markup=True, font_size=35, size_hint_y=None, height=50, outline_width=3)
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
            mvp = OutlinedLabel(text=wrap_text(text=f"{thx['name']}", width=25), markup=True, size_hint_y=None, font_size=30, outline_width=2)
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

