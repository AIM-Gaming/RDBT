from kivy.properties import StringProperty, NumericProperty, ListProperty, OptionProperty
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock

import os

from utils import TEMP_ASSETS_DIR, wrap_text
from log import debug_print
from widgets.outlined_label import OutlinedLabel


class CarouselSelector(BoxLayout):
    items = ListProperty([])
    index = NumericProperty(0)
    selected_item = StringProperty("")

    halign = OptionProperty('auto', options=['left', 'center', 'right', 'justify', 'auto'])
    valign = OptionProperty('bottom', options=['bottom', 'middle', 'top'])


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

        self.display_area = FloatLayout(size_hint_x=1)
        self.display = OutlinedLabel(text=self.selected_item, size_hint=(None, 1), outline_width=2,
                                     halign=self.halign, valign=self.valign,
                                     pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.display.bind(texture_size=self._update_display_width)
        self.display_area.add_widget(self.display)

        self.add_widget(self.left_btn)
        self.add_widget(self.display_area)
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
        
        self._update_display_width(self.display, None)

    def _display_text(self, item):
        """Remove .mp3 extension for display"""
        return wrap_text(text=item.rsplit('.', 1)[0], width=20) if item.lower().endswith('.mp3') else wrap_text(text=item, width=20)
    
    def _update_display_width(self, instance, value):
        # Update width for the instance, add padding
        instance.width = instance.texture_size[0] + 20
    