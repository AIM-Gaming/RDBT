from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

import os
import time
from ffpyplayer.player import MediaPlayer
import pygame

from db import debug_print
from utils import TEMP_ASSETS_DIR


class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.video_path = os.path.join(TEMP_ASSETS_DIR, "videos", "FreeRadsLogoFading.mp4") 
        self.fallback_image_path = os.path.join(TEMP_ASSETS_DIR, "images", "FreeRadsLogo.jpg")
        self.player = None
        self.texture = None
        self.rect = None
    
    def on_enter(self):
        for _ in range(10):
            if os.path.exists(self.video_path) and os.path.getsize(self.video_path) > 1000:
                break
            time.sleep(0.1)
        if os.path.exists(self.video_path):
            self.play_video()
        else:
            debug_print("File path does not exist")
            self.show_fallback_image()
    
    def play_video(self):
        try:
            # Initialize MediaPlayer
            self.player = MediaPlayer(self.video_path)
            self.player.set_pause(True)
            debug_print("Video player initialized successfully.")
            Clock.schedule_once(self._start_video, 0.5)
        except Exception as e:
            debug_print(f"Error initializing MediaPlayer: {e}")
            self.show_fallback_image()
    
    def _start_video(self, dt):
        if self.player:
            self.player.set_pause(False)
            Clock.schedule_once(self.initialize_canvas, 0)
            Clock.schedule_interval(self.update_frame, 1 / 30.0)
    
    # noinspection PyUnusedLocal
    def initialize_canvas(self, dt):
        debug_print(f"Canvas exists: {self.canvas is not None}")
        # Create a texture to display with frames
        with self.canvas.after:
            debug_print("Creating texture...")
            # noinspection PyArgumentList
            self.texture = Texture.create(size=(1440, 1440), colorfmt="rgb")
            self.texture.flip_vertical()
            debug_print("Texture created successfully")
            self.rect = Rectangle(texture=self.texture, size=self.size, pos=self.pos)
        
        self.bind(size=self.update_rect, pos=self.update_rect)
    
    # noinspection PyUnusedLocal
    def update_rect(self, *args):
        if self.rect:
            widget_width, widget_height = self.size
            
            video_width, video_height = 1440, 1440
            
            scale = min(widget_width / video_width, widget_height / video_height)
            new_width, new_height = video_width * scale, video_height * scale
            
            new_x = (widget_width - new_width) / 2
            new_y = (widget_height - new_height) / 2
            
            self.rect.size = (new_width, new_height)
            self.rect.pos = (new_x, new_y)
            debug_print(f"Rectangle updated: Size={self.rect.size}, Pos={self.rect.pos}")
    
    # noinspection PyUnusedLocal
    def update_frame(self, dt):
        if self.player:
            frame, val = self.player.get_frame()
            if frame is not None:
                img, pts = frame
                w, h = img.get_size()
                debug_print(f"Frame pixel format: {img.get_pixel_format()}")
                debug_print(f"Frame updated: PTS={pts}, Resolution={w}x{h}, Frame Bytes={len(img.to_bytearray()[0])}")
                
                # Update the texture with the frame data
                self.texture.blit_buffer(img.to_bytearray()[0], colorfmt="rgb", bufferfmt="ubyte")
                self.rect.texture = self.texture
                
                self.canvas.ask_update()
            
            if val == "eof":
                debug_print("Video playback finished")
                Clock.unschedule(self.update_frame)
                self.transition_to_home()
    
    def transition_to_home(self, dt=None):
        # debug_print("Transitioning to HomeScreen")
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.manager.transition = NoTransition()
        self.manager.current = "HomeScreen"
    
    def show_fallback_image(self):
        fallback_image = Image(source=self.fallback_image_path, size_hint=(1, 1))
        self.add_widget(fallback_image)
        
        # Transition to home after a delay
        Clock.schedule_once(self.transition_to_home, 2)
    
    def on_leave(self, *args):
        if self.player:
            self.player.close_player()  # Close the video player
            # debug_print("Closing video player")
            self.player = None
        if not self.rect:
            debug_print("No rectangle to remove")
            return
        
        try:
            self.canvas.remove(self.rect)
            # debug_print("Rectangle removed successfully")
            self.rect = None
        except ValueError:
            debug_print("Rectangle was not in the canvas")