from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.core.window import Window

import webbrowser


class ClickableLabel(Label):
    normal_color = ListProperty([1, 1, 1, 1])
    hover_color = ListProperty([0.73, 0.56, 0.14, 1])

    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        self.color = self.hover_color if inside else self.normal_color
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.url:
            webbrowser.open(self.url)
            return True
        return super().on_touch_down(touch)
    
    def on_parent(self, instance, value):
        # Ubind when removed from parent to avoid memory leaks
        if value is None:
            Window.unbind(mouse_pos=self.on_mouse_pos)
        else:
            Window.bind(mouse_pos=self.on_mouse_pos)

