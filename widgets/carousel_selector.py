from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock

import os

from utils import TEMP_ASSETS_DIR
from log import debug_print


class CarouselSelector(BoxLayout):
    items = ListProperty([])
    index = NumericProperty(0)
    selected_item = StringProperty("")

    def __init__(self, items=None, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.items = items or []
        self.index = 0
        self.selected_item = self._display_text(self.items[self.index]) if self.items else ""
        self.future_item = self._display_text(self.items[self.index + 1]) if self.items else ""

        self.left_btn = Button(
            background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "LeftArrow.png"),
            background_down=os.path.join(TEMP_ASSETS_DIR, "images", "LeftArrowPressed.png"),
            size_hint=(None, None), width=100, height=100, pos_hint={"center_y": 0.45}
        )
        self.left_btn.bind(on_release=self.previous_item)
        self.right_btn = Button(
            background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "RightArrow.png"),
            background_down=os.path.join(TEMP_ASSETS_DIR, "images", "RightArrowPressed.png"),
            size_hint=(None, None), width=100, height=100, pos_hint={"center_y": 0.45}
        )
        self.right_btn.bind(on_release=self.next_item)

        self.display = Label(text=self.selected_item, size_hint_x=None)
        self.display.bind(texture_size=self._update_display_width)
        self.left_spacer = Widget(size_hint_x=1)
        self.right_spacer = Widget(size_hint_x=1)

        self.add_widget(self.left_btn)
        self.add_widget(self.left_spacer)
        self.add_widget(self.display)
        self.add_widget(self.right_spacer)
        self.add_widget(self.right_btn)

        self.update_display()

    def previous_item(self, *args):
        if self.items:
            self.index = (self.index - 1) % len(self.items)
            self.update_display()

    def next_item(self, *args):
        if self.items:
            self.index = (self.index + 1) % len(self.items)
            self.update_display()

    def update_display(self):
        self.selected_item = self.items[self.index] if self.items else ""
        self.display.text = self._display_text(self.selected_item)

        # self.display.texture_update()
        
        self._update_display_width(self.display, None)

    def _display_text(self, item):
        """Remove .mp3 extension for display"""
        return item.rsplit('.', 1)[0] if item.lower().endswith('.mp3') else item
    
    def _update_display_width(self, instance, value):
        # Dynamically set the label width based on its content
        # Update width for the instance, add padding
        new_width = instance.texture_size[0] + 20  # Padding
        instance.width = new_width
        # Only recenter if this is the main display label
        if instance == self.display and self.parent:
            self.center_to_parent()
    
    def center_to_parent(self, *args):
        if not self.parent:
            return
        
        parent_center = self.parent.to_window(self.parent.center_x, self.parent.center_y)[0]
        display_center = self.display.to_window(self.display.center_x, self.display.center_y)[0]
        shift = (parent_center - display_center) / 2

        self.x += shift
        debug_print(F"Shifted by {shift} pixels")
