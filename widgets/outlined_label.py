from kivy.properties import StringProperty, NumericProperty, ListProperty, OptionProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel


class OutlinedLabel(Widget):
    text = StringProperty("")
    font_size = NumericProperty(30)
    outline_color = ListProperty([0, 0, 0, 1])
    text_color = ListProperty([1, 1, 1, 1])
    outline_width = NumericProperty(0)  # 0 means auto

    halign = OptionProperty('auto', options=['left', 'center', 'right', 'justify', 'auto'])
    valign = OptionProperty('bottom', options=['bottom', 'middle', 'top'])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texture_size = (0, 0)
        self.bind(pos=self._update_canvas, 
                  text=self._update_canvas, 
                  font_size=self._update_canvas,
                  outline_color=self._update_canvas, 
                  text_color=self._update_canvas, 
                  center=self._update_canvas,
                  size=self._update_canvas)
        self._update_canvas()
    
    # noinspection PyUnusedLocal
    def _update_canvas(self, *args):
        self.canvas.clear()
        label = CoreLabel(text=self.text, font_size=self.font_size)
        label.refresh()
        texture = label.texture
        self.texture_size = texture.size
        
        width = int(self.outline_width or (self.font_size * 0.05))
        width = max(1, width)
        
        with (self.canvas):
            for dx in range(-width, width + 1):
                for dy in range(-width, width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    Color(*self.outline_color)
                    Rectangle(texture=texture,
                              pos=(self.center_x - texture.width / 2 + dx,
                                   self.center_y - texture.height / 2 + dy),
                              size=texture.size)
            Color(*self.text_color)
            Rectangle(texture=texture,
                      pos=(self.center_x - texture.width / 2,
                           self.center_y - texture.height / 2),
                      size=texture.size)
