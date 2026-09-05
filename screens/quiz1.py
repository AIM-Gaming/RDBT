from kivy.app import App
from kivy.uix.screenmanager import Screen, NoTransition, FadeTransition
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
# from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window

import os
import random
import requests
from typing import List, Dict, Any

from utils import debug_print, wrap_text, play_sfx, TEMP_ASSETS_DIR, API_BASE_URL
from quiz_manager import QuizManager, fetch_all_questions
from widgets.blurred_image import BlurredImage
from widgets.outlined_label import OutlinedLabel


class QuizOne(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        
        self.background_image = BlurredImage(source=os.path.join(TEMP_ASSETS_DIR, "images", "HomeScreenBackground.png"), allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.background_image)
        
        # Initialize state
        self.quiz_manager = QuizManager(bible_version=App.get_running_app().user_settings.get("bible_version", "NIV"))

        self.timer_event = None
        self.last_question_id = None
        
        self.keyboard = None
        self.selected_button = None
        self.button_hover_colors = {}
        self.flicker_event = None
        self.flicker_state = None
        self.flicker_color = None
        self.original_color = None
        
        # Declare UI variables
        self.timer_label = None
        self.lives_images = {}
        self.question_label = None
        self.result_label = None
        self.start_button = None
        self.pause_button = None
        self.quit_button = None
        
        # UI Elements Setup (labels, buttons etc.)...
        self._setup_ui()
    
    def _setup_ui(self):
        # Timer Label
        self.timer_label = OutlinedLabel(text=f"Time: {self.quiz_manager.time_remaining}", size_hint=(0.3, 0.1),
                                 pos_hint={"x": 0.7, "y": 0.83}, opacity=0, font_size=40,
                                 outline_width=3)
        self.layout.add_widget(self.timer_label)
        
        # Lives Image
        self.lives_images = {
            1: os.path.join(TEMP_ASSETS_DIR, "images", "Lives1Icon.png"),
            2: os.path.join(TEMP_ASSETS_DIR, "images", "Lives2Icon.png"),
            3: os.path.join(TEMP_ASSETS_DIR, "images", "Lives3Icon.png"),
            4: os.path.join(TEMP_ASSETS_DIR, "images", "Lives4Icon.png"),
            5: os.path.join(TEMP_ASSETS_DIR, "images", "Lives5Icon.png")
        }
        self.lives_image = Image(source=self.lives_images[5], size_hint=(None, None),
                                 size=(200, 200), pos_hint={"x": 0.65, "y": 0.8}, opacity=0)
        self.layout.add_widget(self.lives_image)
        
        # Question label
        self.question_label = OutlinedLabel(text="Quiz starting!", size_hint=(0.8, 0.2),
                                            pos_hint={"center_x": 0.5, "center_y": 0.7},
                                            opacity=0, outline_color=[0, 0, 0, 1], text_color=[1, 1, 1, 1])
        self.layout.add_widget(self.question_label)
        
        # Answer buttons grid
        self.answer_layout = GridLayout(cols=2, size_hint=(0.8, 0.3),
                                        pos_hint={"center_x": 0.5, "y": 0.3}, opacity=0)
        self.answer_buttons = {}
        for name in ["A", "B", "C", "D"]:
            btn = Button(text=f"Option {name}", size_hint=(1, 1), opacity=0)
            self.answer_buttons[name] = btn
            self.answer_layout.add_widget(btn)
        self.layout.add_widget(self.answer_layout)
        
        # Result label
        self.result_label = OutlinedLabel(text="Result Goes Here", halign='center', valign='middle',
                                        size_hint=(0.8, 0.1), pos_hint={"center_x": 0.5, "y": 0.2}, opacity=0)
        self.layout.add_widget(self.result_label)
        
        # Quit button
        self.quit_button = Button(size_hint=(None, None), pos_hint={"center_x": 0.5, "y": 0.1},
                                  background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "HomeButton.png"),
                                  background_down=os.path.join(TEMP_ASSETS_DIR, "images", "HomeButtonPressed.png"),
                                  border=(0, 0, 0, 0), size=(150, 150))
        self.quit_button.bind(on_release=self.go_home)
        self.layout.add_widget(self.quit_button)

        # Pause button
        self.pause_button = Button(size_hint=(None, None), pos_hint={"x": 0.05, "y": 0.85}, size=(100, 100), 
                                   background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "PauseButton.png"), 
                                   background_down=os.path.join(TEMP_ASSETS_DIR, "images", "PauseButtonPressed.png"), 
                                   border=(0, 0, 0, 0), opacity=0, disabled=True)
        self.pause_button.bind(on_release=self.confirm_quit)
        self.layout.add_widget(self.pause_button)
        
        # Start button
        self.start_button = Button(size_hint=(None, None), size=(320, 180), pos_hint={"center_x": 0.5, "center_y": 0.5},
                                   background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "StartButton.png"),
                                   background_down=os.path.join(TEMP_ASSETS_DIR, "images", "StartButtonPressed.png"),
                                   border=(0, 0, 0, 0), opacity=100)
        self.start_button.bind(on_release=self.start_quiz)
        self.layout.add_widget(self.start_button)
    
    def go_home(self, instance):
        if self.quiz_manager.game_over and self.quiz_manager.lives == 0:
            debug_print("End of game. Returning to home screen.")
            self.reset(reset_db=True)
            self.update_lives_display()
        self.manager.transition = NoTransition()
        self.manager.current = "HomeScreen"
    
    def on_pre_enter(self):
        self.lives_image.opacity = 0
    
    def on_enter(self):
        # home_screen = self.manager.get_screen("HomeScreen")
        # home_screen.stop_music(None)
        # if home_screen.player:
        #     home_screen.player = None
        
        self.keyboard = Window.request_keyboard(lambda: setattr(self, "keyboard", None), self)
        if self.keyboard:
            self.keyboard.bind(on_key_down=self.on_key_down)
    
    def on_leave(self):
        if self.keyboard:
            self.keyboard.unbind(on_key_down=self.on_key_down)
            self.keyboard = None
        
        # Save progress when leaving the quiz
        if not self.quiz_manager.game_over:
            self.quiz_manager.save_progress()
            debug_print("Progress saved on leaving the quiz")

        if self.timer_event:
            self.timer_event.cancel()
    
    # noinspection PyUnusedLocal
    def start_quiz(self, instance):
        debug_print("start_quiz() accessed")
        self.quiz_manager.game_over = False
        self.quiz_manager.current_question_index = 0
        
        self._show_ui_elements()
        conn = None
        cursor = None
        
        try:
            user_id = App.get_running_app().user_id

            response = requests.get(f"{API_BASE_URL}/users/{user_id}/lim_progress")
            response.raise_for_status()
            progress = response.json()
            
            debug_print(f"Time remaining: {progress['time_remaining']} | Score: {progress['score']}")
            if progress and (progress["time_remaining"] < 30 or progress["score"] > 0):
                self.load_progress(progress)
            else:
                self.quiz_manager.load_questions(shuffle=True, limit=self.quiz_manager.num_questions_per_round)
                self.setup_question()
        except requests.RequestException as e:
            debug_print(f"Error fetching progress from API: {e}")
    
    def _show_ui_elements(self):
        self.start_button.opacity = 0  # Hide start button
        self.start_button.disabled = True
        self.start_button.pos_hint = {"center_x": -1, "center_y": -1}

        self.pause_button.opacity = 100
        self.pause_button.disabled = False
        self.pause_button.pos_hint = {"x": 0.05, "y": 0.85}

        self.quit_button.opacity = 0  # Hide quit button
        self.quit_button.disabled = True
        self.quit_button.pos_hint = {"center_x": -2, "center_y": -2}
        
        self.timer_label.opacity = 100  # Show all other widgets
        self.lives_image.opacity = 100
        self.question_label.opacity = 100
        self.result_label.opacity = 100
        self.answer_layout.opacity = 100
    
    def load_progress(self, progress):
        debug_print("load_progress() accessed")
        if self.timer_event:
            self.timer_event.cancel()
        
        q = self.quiz_manager
        
        q.current_bank_index = progress["current_bank_index"]
        q.current_question_index = progress["current_question"]
        q.score = progress["score"]
        q.lives = progress["lives"]
        q.time_remaining = max(progress["time_remaining"], 10)  # This loads time properly
        q.last_question_id = progress.get("last_question")
        
        q.load_questions(shuffle=False, limit=None)
        
        if q.current_question_index >= len(q.questions):
            debug_print(f"Question index {q.current_question_index} exceeds available questions, resetting to 0.")
            q.current_question_index = 0
        
        self.timer_label.text = f"Time: {q.time_remaining}"  # This shows the correct time
        self.update_lives_display()
        self.setup_question()
    
    # noinspection PyUnusedLocal
    def setup_question(self, dt=None):
        print("setup_question() accessed")
        q = self.quiz_manager
        
        if q.current_question_index >= len(q.questions):
            debug_print("User is at the end of the round")
            debug_print(f"Question index: {q.current_question_index}")
            if q.current_bank_index == 4:  # If the user is at the end of round 4
                debug_print("User is at the end of round 4")
                if q.score < 230:   # And hasn't met the score threshold
                    debug_print("User has not met the threshold")
                    q.game_over = True
                    self.check_game_over()
                else:  # User met the score threshold, allow round 5
                    debug_print("User met the threshold")
                    self.quiz_manager.num_questions_per_round = 15
                    self.next_round()
            else:  # Move to the next round if not at round 4
                debug_print("Game will move on to the next round")
                response = requests.get(f"{API_BASE_URL}/bible_trivia/get_last_round")
                response.raise_for_status()
                last_round = response.json()
                
                if q.current_bank_index + 1 > last_round:
                    q.game_over = True
                    self.check_game_over()
                else:
                    self.next_round()
        else:
            debug_print("Show the next question in the round")
            self.show_question()
    
    def show_question(self):
        debug_print("show_question() accessed")
        self._reset_buttons()  # Reset buttons first
        user_id = App.get_running_app().user_id
        
        if self.flicker_event:
            Clock.unschedule(self.flicker_event)
            self.flicker_event = None
        if self.timer_event:
            self.timer_event.cancel()
        
        if self.quiz_manager.game_over:
            return
        
        # Select the next question from the available ones
        question_data = self.quiz_manager.get_current_question()
        self.quiz_manager.last_question_id = question_data["question_id"]
        self.quiz_manager.used_question_ids.add(self.quiz_manager.last_question_id)

        debug_print(f"Now showing question_id: {self.quiz_manager.last_question_id} at index {self.quiz_manager.current_question_index}")

        question_text = question_data["question_text"]
        answers: List[Dict[str, Any]] = question_data["answers"]
        correct_answers = [ans for ans in answers if ans["is_correct"]]
        incorrect_answers = [ans for ans in answers if not ans["is_correct"]]
        answer_references = {ans["answer_text"]: ans["bible_ref"] for ans in incorrect_answers}
        
        # Design adjustments and result label reset
        self.result_label.text = ""
        self.result_label.font_size = 30
        self.question_label.font_size = 36
        self.question_label.text = wrap_text(question_text, 80)
        
        if correct_answers:
            chosen_correct = random.choice(correct_answers)
            selected_correct = [chosen_correct["answer_text"]]
            debug_print(f"Randomly selected correct answer for options: {chosen_correct['answer_text']}")
        else:
            debug_print("ERROR: NO CORRECT ANSWERS")
            selected_correct = []  # Edge case for when there are no correct answers (shouldn't happen)
        
        num_options = min(4, len(correct_answers) + len(incorrect_answers))
        selected_incorrect = random.sample(
            [ans["answer_text"] for ans in incorrect_answers],
            num_options - len(selected_correct)
        )
        
        final_answers = selected_correct + selected_incorrect
        random.shuffle(final_answers)
        
        # ✅ Define button colors (normal, hover)
        button_colors = [
            ([0, 0, 0.7, 1], [0, 0, 0.8, 1]),  # Blue
            ([0.7, 0, 0, 1], [0.8, 0, 0, 1]),  # Red
            ([0, 0.7, 0, 1], [0, 0.8, 0, 1]),  # Green
            ([0.7, 0.7, 0, 1], [0.8, 0.8, 0, 1])  # Yellow
        ]
        
        self.button_hover_colors = {}
        
        # Apply colors and store buttons
        button_index = 1
        for i, (button, answer) in enumerate(zip(self.answer_buttons.values(), final_answers)):
            button.text = wrap_text(answer, 40)
            button.opacity = 1
            button.disabled = False
            
            is_correct = answer in selected_correct
            scripture_ref = answer_references.get(answer, "")
            button.on_press = lambda btn=button, correct=is_correct, ref=scripture_ref, ans=answer: self._handle_button_press(btn, correct, ref, ans)
            debug_print(f"---------------\nButton #{button_index} answer: {answer}\n---------------")
            button_index += 1
            
            # Apply colors
            button.background_normal = ""
            button.background_down = ""
            normal_color, hover_color = button_colors[i % len(button_colors)]
            hover_color_str = (f"rgba({int(hover_color[0] * 255)}, {int(hover_color[1] * 255)}, "
                               f"{int(hover_color[2] * 255)}, {hover_color[3]})")
            button.background_color = normal_color
            button.background_down = hover_color_str
            self.button_hover_colors[button] = hover_color_str
        
        # ✅ Hide unused buttons (e.g., for True/False questions)
        for btn_name in list(self.answer_buttons.keys())[len(final_answers):]:
            self.answer_buttons[btn_name].opacity = 0
            self.answer_buttons[btn_name].disabled = True
            self.answer_buttons[btn_name].text = ""
        
        try:
            response = requests.get(f"{API_BASE_URL}/users/{user_id}/get_last_question")
            response.raise_for_status()
            saved_question_id = response.json()

            if question_data['question_id'] != saved_question_id:
                self.quiz_manager.time_remaining = 30
            else:
                self.quiz_manager.time_remaining = max(self.quiz_manager.time_remaining, 10)
            self.timer_label.text = f"Time: {self.quiz_manager.time_remaining}"
            self.start_timer()
        except requests.RequestException as e:
            debug_print(f"Error fetching last question ID: {e}")
    
    def _handle_button_press(self, button, is_correct, scripture_references, answer):
        self.selected_button = button
        debug_print(f"------------\nAnswer passed to check_answer(): {answer}\n------------")
        self.check_answer(is_correct, scripture_references, answer)

    def _reset_buttons(self):
        for btn in self.answer_buttons.values():
            btn.opacity = 100
            btn.disabled = True
            btn.text = ""
            btn.on_press = None
    
    # noinspection PyUnusedLocal
    def on_key_down(self, keyboard, keycode, text, modifiers):
        """Handles key press events for answer selection."""
        key = keycode[1]  # Get the key as a string (e.g., "1", "2", "3", "4")
        
        if key in ["1", "2", "3", "4"]:  # Ensure a valid key is pressed
            btn_keys = list(self.answer_buttons.keys())  # Get button keys
            
            if int(key) - 1 < len(btn_keys):  # Ensure the index is valid
                self.selected_button = self.answer_buttons[btn_keys[int(key) - 1]]
                selected_btn = self.selected_button
                
                if not selected_btn.disabled:  # Prevent selecting disabled buttons
                    selected_btn.trigger_action(duration=0)  # Simulate button press
                    hover_color = self.button_hover_colors[selected_btn]
                    selected_btn.background_down = hover_color
        
        return True  # Consume the event
    
    def start_timer(self):
        debug_print("start_timer() accessed")
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
    
    # noinspection PyUnusedLocal
    def update_timer(self, dt=None):
        if self.quiz_manager.time_remaining > 0:
            self.quiz_manager.time_remaining -= 1
            self.timer_label.text = f"Time: {self.quiz_manager.time_remaining}"
        else:
            if self.timer_event:
                self.timer_event.cancel()
            self.time_up()
    
    def time_up(self):
        debug_print("Time's up!")
        self.result_label.text = "Time's up!"
        self.quiz_manager.lives -= 1
        self.update_lives_display()
        Clock.schedule_once(self.time_up_effect, 1)
    
    # noinspection PyUnusedLocal
    def time_up_effect(self, dt=None):
        if self.quiz_manager.lives <= 0:
            self.quiz_manager.game_over = True
            self.check_game_over()
        else:
            self.quiz_manager.next_question()
            if self.quiz_manager.game_over:
                self.check_game_over()
                return
            
            self.quiz_manager.time_remaining = 30
            debug_print(f"time_up_effect(): {self.quiz_manager.current_question_index}")
            self.setup_question()
    
    def update_lives_display(self):
        lives = self.quiz_manager.lives
        if lives > 0:
            self.lives_image.source = self.lives_images.get(lives, self.lives_images[5])
            self.lives_image.opacity = 100
        else:
            self.lives_image.opacity = 0
    
    # noinspection PyUnusedLocal
    def flicker_button(self, dt):
        if not self.selected_button:
            return
        
        self.flicker_state = not self.flicker_state  # Toggle flicker state
        self.selected_button.background_color = self.flicker_color if self.flicker_state else self.original_color
    
    # noinspection PyUnusedLocal
    def check_answer(self, is_correct, scripture_references=None, selected_text=None):
        """Checks if the answer provided by the user is correct."""
        debug_print("check_answer() accessed")
        if self.timer_event:
            self.timer_event.cancel()
        
        for btn in self.answer_buttons.values():  # Disable the buttons after selecting an answer
            btn.disabled = True
        
        selected_btn = self.selected_button
        if not selected_btn:
            return
        
        self.flicker_color = [0, 1, 0, 1] if is_correct else [1, 0, 0, 1]  # Flicker green if correct else flicker red
        self.original_color = selected_btn.background_color
        
        self.flicker_state = False  # Tracks whether to use original color or flicker color
        self.flicker_event = Clock.schedule_interval(self.flicker_button, 0.2)
        
        result = self.quiz_manager.check_answer(selected_text)
        
        # Check if the selected answer is correct
        if result["is_correct"]:
            play_sfx("correct_answer_1.mp3")
            self.result_label.text = "Correct!"
        else:
            play_sfx("wrong_answer_1.mp3")
            self.result_label.text = "Shame."
            self.update_lives_display()
        
        if result["scripture_references"] and not result["is_correct"]:
            if isinstance(result["scripture_references"], str):
                scripture_references = [result["scripture_references"]]
            else:
                scripture_references = [ref for ref in result["scripture_references"] if ref is not None]
            debug_print(f"Scripture references: {scripture_references}")
            
            self.result_label.text += f" [{' | '.join(scripture_references)}]"
        elif result["is_correct"]:
            debug_print("No scripture reference needed for correct answer")
        else:
            debug_print("No scripture reference exists")
        
        if self.quiz_manager.is_game_over():
            debug_print("Checking game over")
            self.check_game_over()
        else:
            Clock.schedule_once(self.setup_question, 2)
    
    def next_round(self):
        debug_print("next_round() accessed")
        self.result_label.text = f"Round {self.quiz_manager.current_bank_index} completed!"
        if self.quiz_manager.current_bank_index == 4 and self.quiz_manager.score >= 230:
            Clock.schedule_once(self._delay_before_next_round, 2)
        else:
            Clock.schedule_once(lambda dt: self.finalize_next_round(), 2)
    
    def _delay_before_next_round(self, dt):
        self.result_label.text = "230-point threshold crossed! Advancing to Round 5. Get ready..."
        Clock.schedule_once(lambda dt: self.finalize_next_round(), 2)
    
    def finalize_next_round(self):
        # Check if there's a next round before incrementing
        debug_print("finalize_next_round() accessed")
        try:
            response = requests.get(f"{API_BASE_URL}/bible_trivia/get_last_round")
            response.raise_for_status()
            last_round = response.json()
        except requests.RequestException as e:
            debug_print(f"Error fetching last round: {e}")
        if self.quiz_manager.current_bank_index < last_round:
            debug_print("There are more rounds to play, moving to the next round")
            self.quiz_manager.current_bank_index += 1

            # Generate a new set of questions for the new round
            self.quiz_manager.questions = fetch_all_questions(
                bank_id=self.quiz_manager.current_bank_index,
                shuffle=True,
                limit=self.quiz_manager.num_questions_per_round,
                selected_bible_version=self.quiz_manager.bible_version
            ) or []
            self.quiz_manager.current_question_index = 0
            self.quiz_manager.save_progress()  # Save the new questions id list
            debug_print("setup_question() called in finalize_next_round()")
            self.setup_question()
        else:
            debug_print("No more rounds available, game over.")
            # No more rounds, end the game
            self.quiz_manager.game_over = True
            self.check_game_over()
    
    def check_game_over(self, user_id=None):
        """Checks whether the game is over or the quiz is completed"""
        debug_print("check_game_over() accessed")
        user_id = user_id or App.get_running_app().user_id
        score = self.quiz_manager.score
        lives = self.quiz_manager.lives
        bank_index = self.quiz_manager.current_bank_index
        
        # Get high score from database
        try:
            response = requests.get(f"{API_BASE_URL}/users/{user_id}/high_score")
            high_score = response.json() if response.status_code == 200 else 0

            self.result_label.pos_hint = {"y": 0.5}

            self.quit_button.pos_hint = {"center_x": 0.5, "y": 0.1}
            self.quit_button.size = (150, 150)
            self.quit_button.disabled = False
            self.quit_button.opacity = 100
            self.quit_button.background_normal = os.path.join(TEMP_ASSETS_DIR, "images", "HomeButton.png")
            self.quit_button.background_down = os.path.join(TEMP_ASSETS_DIR, "images", "HomeButtonPressed.png")
            
            if lives <= 0:  # If player ran out of lives
                debug_print("Player has run out of lives")
                self.result_label.text = (f"Read your Bible.\n Your score: {score}\n Lives: {lives}\n High Score: {high_score}")
            elif bank_index == 4 and score < 230:  # If player didn't meet score threshold for round 5
                debug_print("Player did not meet score threshold for Round 5")
                self.result_label.text = f"Quiz completed!\n Your score: {score}\n Lives: {lives}\n High Score: {high_score}\nYou need at least 230 points to advance to Round 5!"
            else:  # Quiz completed successfully
                debug_print("Quiz completed successfully")
                self.result_label.text = f"Quiz completed!\n Your score: {score}\n Lives: {lives}\n High Score: {high_score}"

            # Prevent the resume button from appearing
            home_screen = self.manager.get_screen("HomeScreen")
            home_screen.has_left_game_this_session = False
            
            # Update high score if beaten
            if score > high_score:
                rsp = requests.post(f"{API_BASE_URL}/users/{user_id}/update_high_score", json={"score": score})
                rsp.raise_for_status()
                if rsp.status_code == 200:
                    self.result_label.text += "\nNew High Score!"
                else:
                    debug_print(f"Error updating high score: {rsp.json().get('message')}")
        except requests.RequestException as e:
            debug_print(f"API error in check_game_over(): {e}")
        
        # Disable all UI elements
        self.question_label.opacity = 0
        self.lives_image.opacity = 0
        self.timer_label.opacity = 0
        self.pause_button.opacity = 0
        
        for btn in self.answer_buttons.values():
            btn.opacity = 0
            btn.disabled = True
            btn.text = ""
            btn.on_press = None
        debug_print("Game over. No more questions.")
    
    # noinspection PyUnusedLocal
    def confirm_quit(self, *args):
        in_progress = (not self.quiz_manager.game_over)
        if in_progress:
            debug_print("Confirming quit during an in-progress game.")
            if self.timer_event:
                self.timer_event.cancel()
            
            content = BoxLayout(orientation="vertical")
            content.add_widget(Label(text="Do you want to quit? Your progress will be saved."))

            self._quit_confirmed = False

            def on_yes(*_args):
                self._quit_confirmed = True
                popup.dismiss()
                self.quit_quiz()

            def on_no(*_args):
                popup.dismiss()
                self.start_timer()
            
            button_box = BoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height=180)
            button_box.add_widget(Widget(size_hint_x=1))
            button_box.add_widget(Button(
                size_hint=(None, None), size=(320, 180),
                background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "YesButton.png"), 
                background_down=os.path.join(TEMP_ASSETS_DIR, "images", "YesButtonPressed.png"), 
                on_release=on_yes
                ))
            button_box.add_widget(Button(
                size_hint=(None, None), size=(320, 180),
                background_normal=os.path.join(TEMP_ASSETS_DIR, "images", "NoButton.png"), 
                background_down=os.path.join(TEMP_ASSETS_DIR, "images", "NoButtonPressed.png"), 
                on_release=on_no
                ))
            button_box.add_widget(Widget(size_hint_x=1))

            content.add_widget(button_box)
            
            popup = Popup(title="", content=content, size_hint=(0.4, 0.3))

            def on_popup_dismiss(*_args):  # Continue the paused timer if user just dismisses the popup
                if not getattr(self, "_quit_confirmed", False):
                    self.start_timer()
                self._quit_confirmed = False
            
            popup.bind(on_dismiss=on_popup_dismiss)
            popup.open()
        elif not in_progress and self.quiz_manager.lives == 0:
            debug_print("End of game. Returning to home screen.")
            self.reset(reset_db=True)
            home_page = self.manager.get_screen("HomeScreen")
            home_page.update_button_box()
            self.manager.transition = FadeTransition()
            self.manager.current = "HomeScreen"
        else:
            debug_print("Returning to home screen before starting quiz.")
            home_page = self.manager.get_screen("HomeScreen")
            home_page.update_button_box()
            self.manager.transition = FadeTransition()
            self.manager.current = "HomeScreen"
    
    # noinspection PyUnusedLocal
    def quit_quiz(self, *args):
        current_question = self.quiz_manager.get_current_question()
        if current_question:
            self.quiz_manager.last_question_id = current_question["question_id"]
        self.quiz_manager.save_progress()
        self.reset(reset_db=False)

        home_page = self.manager.get_screen("HomeScreen")
        home_page.has_left_game_this_session = True
        home_page.update_button_box()
        self.manager.transition = NoTransition()
        self.manager.current = "HomeScreen"
    
    # noinspection PyUnusedLocal
    def reset(self, instance=None, reset_db=True):
        debug_print("Resetting game")
        if self.timer_event:
            self.timer_event.cancel()  # Cancel any running timers
        
        q = self.quiz_manager
        user_id = App.get_running_app().user_id
        
        q.used_question_ids = set()
        
        self.timer_label.text = f"Time: {self.quiz_manager.time_remaining}"
        self.result_label.text = ""
        
        self.timer_label.opacity = 0
        self.result_label.opacity = 0
        self.result_label.pos_hint = {"center_x": 0.5, "y": 0.2}
        self.question_label.opacity = 0
        self.answer_layout.opacity = 0
        
        if reset_db:
            try:
                response = requests.post(f"{API_BASE_URL}/users/{user_id}/reset_progress")
                response.raise_for_status()

                q.current_bank_index = 1
                q.current_question_index = 0
                q.score = 0
                q.lives = 4
                q.time_remaining = 30
                q.last_question_id = None
                q.num_questions_per_round = 6
                q.used_question_ids = set()
                debug_print(f"Progress reset!\n\tBank index: {q.current_bank_index}\n\tQuestion index: {q.current_question_index}\n\tScore: {q.score}\n\tLives: {q.lives}\n\tTime remaining: {q.time_remaining}\n\tLast question ID (should be none): {q.last_question_id}\n\tQuestion ID list (should be an empty set): {q.used_question_ids}")
            except requests.RequestException as e:
                debug_print(f"API error in reset(): {e}")
        
        self.update_lives_display()
        self.start_button.opacity = 100
        self.start_button.disabled = False
        self.start_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.quit_button.pos_hint = {"center_x": 0.5, "y": 0.1}
        self.quit_button.size_hint = (None, None)
        self.quit_button.size = (150, 150)
        self.quit_button.background_normal = os.path.join(TEMP_ASSETS_DIR, "images", "HomeButton.png")
        self.quit_button.background_down = os.path.join(TEMP_ASSETS_DIR, "images", "HomeButtonPressed.png")
