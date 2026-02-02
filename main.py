"""Brain Training App - Main application file."""
import os
import logging

# Suppress clipboard warnings before Kivy initialization
# Use CRITICAL to completely suppress Cutbuffer logger messages
logging.getLogger('Cutbuffer').setLevel(logging.CRITICAL)

# Configure Kivy before importing other Kivy modules
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_CLIPBOARD'] = 'dummy'  # Use dummy clipboard to avoid xclip dependency

from kivy import Config
# Don't exit on escape, we'll handle it ourselves
Config.set('kivy', 'exit_on_escape', '0')
# Set log level to warning to suppress info messages
Config.set('kivy', 'log_level', 'warning')

import random
import time
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.core.audio import SoundLoader
from database import Database
import json

# Keyboard key codes
KEYCODE_ENTER = 13
KEYCODE_ESCAPE = 27

# UI timing constants
FOCUS_DELAY = 0.1  # Small delay to ensure UI is ready before setting focus

# Unlimited time constant
UNLIMITED_TIME = 0  # 0 means unlimited time (no countdown timer)

# Text-to-speech support
try:
    from gtts import gTTS
    import os
    import tempfile
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class MainScreen(Screen):
    """Main menu screen with statistics."""
    
    stats_text = StringProperty("Loading statistics...")
    
    def on_enter(self):
        """Called when entering the screen."""
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display."""
        db = Database()
        stats = db.get_statistics()
        
        self.stats_text = (
            f"Total Sessions: {stats['total_sessions']}\n"
            f"Total Questions: {stats['total_questions']}\n"
            f"Correct Answers: {stats['correct_answers']}\n"
            f"Accuracy: {stats['accuracy']:.1f}%"
        )


class NewTrainScreen(Screen):
    """Screen for starting a new training session."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.difficulty = "Easy"
        self.time_per_question = 10
    
    def set_difficulty(self, difficulty):
        """Set training difficulty."""
        self.difficulty = difficulty
    
    def set_time(self, time_str):
        """Set time per question."""
        try:
            if time_str == 'Unlimited':
                self.time_per_question = UNLIMITED_TIME
            else:
                # Extract number from "X seconds" format
                self.time_per_question = int(time_str.split()[0])
        except (ValueError, IndexError):
            self.time_per_question = 10
    
    def start_training(self):
        """Start the training session."""
        app = App.get_running_app()
        training_screen = app.root.get_screen('training')
        
        if self.difficulty == 'Custom':
            # Get custom range values from UI
            min_input = self.ids.get('min_range_input')
            max_input = self.ids.get('max_range_input')
            
            try:
                min_range = int(min_input.text) if min_input and min_input.text else 0
                max_range = int(max_input.text) if max_input and max_input.text else 10
            except (ValueError, AttributeError):
                min_range = 0
                max_range = 10
            
            training_screen.setup_custom_training(min_range, max_range, self.time_per_question)
        else:
            training_screen.setup_training(self.difficulty, self.time_per_question)
        
        app.root.current = 'training'


class TrainingScreen(Screen):
    """Screen for training session."""
    
    question_text = StringProperty("5 x 10 = ?")
    timer_text = StringProperty("Time: 10")
    score_text = StringProperty("Score: 0/0")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_num1 = 0
        self.current_num2 = 0
        self.correct_answer = 0
        self.remaining_time = 10
        self.time_per_question = 10
        self.difficulty = "Easy"
        self.min_range = 0
        self.max_range = 10
        self.total_questions = 0
        self.correct_answers = 0
        self.timer_event = None
        self.current_sound = None
        self.current_temp_file = None
    
    def setup_training(self, difficulty, time_per_question):
        """Setup training parameters."""
        self.difficulty = difficulty
        self.time_per_question = time_per_question
        self.remaining_time = time_per_question
        self.total_questions = 0
        self.correct_answers = 0
        
        # Set number ranges based on difficulty
        if difficulty == "Easy":
            self.min_range = 0
            self.max_range = 10
        elif difficulty == "Medium":
            self.min_range = 10
            self.max_range = 20
        elif difficulty == "Hard":
            self.min_range = 20
            self.max_range = 100
        
        self.generate_question()
        self.start_timer()
    
    def setup_custom_training(self, min_range, max_range, time_per_question):
        """Setup custom training parameters."""
        self.difficulty = "Custom"
        self.min_range = min_range
        self.max_range = max_range
        self.time_per_question = time_per_question
        self.remaining_time = time_per_question
        self.total_questions = 0
        self.correct_answers = 0
        
        self.generate_question()
        self.start_timer()
    
    def generate_question(self):
        """Generate a new question."""
        self.current_num1 = random.randint(self.min_range, self.max_range)
        self.current_num2 = random.randint(self.min_range, self.max_range)
        self.correct_answer = self.current_num1 * self.current_num2
        
        self.question_text = f"{self.current_num1} x {self.current_num2} = ?"
        self.score_text = f"Score: {self.correct_answers}/{self.total_questions}"
        
        # Clean up previous audio if still playing
        if self.current_sound:
            self.current_sound.stop()
        if self.current_temp_file:
            self._cleanup_temp_file(self.current_temp_file)
        
        # Speak the question if voice is enabled
        app = App.get_running_app()
        if app.voice_enabled and TTS_AVAILABLE:
            try:
                # Create speech text
                speech_text = f"{self.current_num1} times {self.current_num2}"
                
                # Generate speech audio file
                tts = gTTS(text=speech_text, lang='en', slow=False)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                
                # Play the audio file using Kivy's SoundLoader
                sound = SoundLoader.load(temp_file)
                if sound:
                    self.current_sound = sound
                    self.current_temp_file = temp_file
                    
                    # Bind to on_stop event to clean up after playback
                    sound.bind(on_stop=lambda instance: self._cleanup_temp_file(temp_file))
                    sound.play()
                else:
                    # If sound loading fails, clean up immediately
                    self._cleanup_temp_file(temp_file)
            except Exception:
                # Silently fail if TTS doesn't work
                pass
        
        # Set focus on answer input field
        Clock.schedule_once(lambda dt: self.focus_answer_input(), FOCUS_DELAY)
    
    def _cleanup_temp_file(self, filepath):
        """Clean up temporary audio file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            if self.current_temp_file == filepath:
                self.current_temp_file = None
        except Exception:
            pass
    
    def start_timer(self):
        """Start the countdown timer."""
        self.remaining_time = self.time_per_question
        
        # Handle unlimited time mode
        if self.time_per_question == UNLIMITED_TIME:
            self.timer_text = "Time: ∞"
            # Don't start a countdown timer
            if self.timer_event:
                self.timer_event.cancel()
            return
        
        self.timer_text = f"Time: {self.remaining_time}"
        
        if self.timer_event:
            self.timer_event.cancel()
        
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
    
    def update_timer(self, dt):
        """Update the countdown timer."""
        self.remaining_time -= 1
        self.timer_text = f"Time: {self.remaining_time}"
        
        if self.remaining_time <= 0:
            self.check_answer("")
    
    def check_answer(self, answer):
        """Check the user's answer."""
        if self.timer_event:
            self.timer_event.cancel()
        
        self.total_questions += 1
        
        try:
            user_answer = int(answer) if answer else -1
        except ValueError:
            user_answer = -1
        
        if user_answer == self.correct_answer:
            self.correct_answers += 1
            # For correct answers, automatically go to next question without popup
            # This provides faster feedback and keeps the training flow smooth
            self.generate_question()
            self.start_timer()
        else:
            # For wrong answers, show popup with correct answer and wait for user action
            result_text = f"Wrong! The answer was {self.correct_answer}"
            self.show_result_popup(result_text)
    
    def show_result_popup(self, result_text):
        """Show result popup with keyboard navigation support."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=result_text, size_hint=(1, 0.7)))
        
        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
        
        next_btn = Button(text='Next Question (Enter)')
        end_btn = Button(text='End Training (Esc)')
        
        popup = Popup(title='Result', content=content, size_hint=(0.8, 0.4))
        
        # Track if handler is bound to prevent double unbinding
        handler_bound = [True]  # Use list for mutable closure variable
        
        def unbind_handler():
            """Safely unbind the keyboard handler if still bound."""
            if handler_bound[0]:
                Window.unbind(on_keyboard=handle_keyboard)
                handler_bound[0] = False
        
        def cleanup_and_next():
            """Unbind keyboard and proceed to next question."""
            unbind_handler()
            popup.dismiss()
            self.generate_question()
            self.start_timer()
        
        def cleanup_and_end():
            """Unbind keyboard and end training."""
            unbind_handler()
            popup.dismiss()
            self.end_training_session()
        
        def handle_keyboard(instance, key, scancode, codepoint, modifier):
            """Handle keyboard input in popup.
            
            Note: This handler unbinds itself before taking action to prevent
            memory leaks and ensure clean lifecycle management.
            """
            if key == KEYCODE_ENTER:
                cleanup_and_next()
                return True
            elif key == KEYCODE_ESCAPE:
                cleanup_and_end()
                return True
            return False
        
        # Button handlers use the same cleanup functions
        next_btn.bind(on_press=lambda instance: cleanup_and_next())
        end_btn.bind(on_press=lambda instance: cleanup_and_end())
        
        btn_layout.add_widget(next_btn)
        btn_layout.add_widget(end_btn)
        content.add_widget(btn_layout)
        
        # Bind keyboard immediately (before popup opens) to handle all cases
        Window.bind(on_keyboard=handle_keyboard)
        # Unbind on dismiss as safety cleanup for any programmatic dismissals
        popup.bind(on_dismiss=lambda instance: unbind_handler())
        
        popup.open()
    
    def end_training_session(self):
        """End the training session and save results."""
        if self.timer_event:
            self.timer_event.cancel()
        
        # Clean up audio
        if self.current_sound:
            self.current_sound.stop()
        if self.current_temp_file:
            self._cleanup_temp_file(self.current_temp_file)
        
        # Save to database
        if self.total_questions > 0:
            db = Database()
            db.add_training_session(
                self.difficulty,
                self.total_questions,
                self.correct_answers,
                self.time_per_question
            )
        
        # Return to main screen
        app = App.get_running_app()
        app.root.current = 'main'
    
    def on_enter(self):
        """Called when entering the screen."""
        Window.bind(on_keyboard=self.handle_keyboard)
        # Set focus on answer input field when entering the screen
        Clock.schedule_once(lambda dt: self.focus_answer_input(), FOCUS_DELAY)
    
    def focus_answer_input(self):
        """Set focus on the answer input field."""
        if hasattr(self, 'ids') and 'answer_input' in self.ids:
            self.ids.answer_input.focus = True
    
    def on_leave(self):
        """Called when leaving the screen."""
        Window.unbind(on_keyboard=self.handle_keyboard)
        if self.timer_event:
            self.timer_event.cancel()
        
        # Clean up audio
        if self.current_sound:
            self.current_sound.stop()
        if self.current_temp_file:
            self._cleanup_temp_file(self.current_temp_file)
    
    def handle_keyboard(self, instance, key, scancode, codepoint, modifier):
        """Handle keyboard input during training."""
        if key == KEYCODE_ESCAPE:
            self.end_training_session()
            return True
        return False


class SettingsScreen(Screen):
    """Settings screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_min = 0
        self.custom_max = 10
        self.custom_time = 10


class BrainTrainerApp(App):
    """Main application class."""
    
    voice_enabled = BooleanProperty(False)
    theme_mode = StringProperty('light')  # 'light' or 'dark'
    
    # Theme colors
    theme_colors = DictProperty({
        'light': {
            'bg_primary': [0.96, 0.97, 0.98, 1],      # Very light gray-blue
            'bg_secondary': [1, 1, 1, 1],              # White
            'bg_card': [1, 1, 1, 1],                   # White
            'text_primary': [0.13, 0.13, 0.13, 1],     # Dark gray
            'text_secondary': [0.4, 0.4, 0.4, 1],      # Medium gray
            'button_bg': [0.2, 0.51, 0.96, 1],         # Modern blue
            'button_text': [1, 1, 1, 1],               # White
            'button_bg_alt': [0.29, 0.76, 0.55, 1],    # Modern green
            'accent': [0.5, 0.31, 0.94, 1],            # Purple accent
            'border': [0.88, 0.89, 0.9, 1],            # Light border
        },
        'dark': {
            'bg_primary': [0.11, 0.11, 0.13, 1],       # Very dark gray
            'bg_secondary': [0.15, 0.15, 0.17, 1],     # Dark gray
            'bg_card': [0.18, 0.18, 0.21, 1],          # Card background
            'text_primary': [0.95, 0.95, 0.96, 1],     # Almost white
            'text_secondary': [0.65, 0.65, 0.67, 1],   # Light gray
            'button_bg': [0.27, 0.53, 0.95, 1],        # Modern blue
            'button_text': [1, 1, 1, 1],               # White
            'button_bg_alt': [0.29, 0.76, 0.55, 1],    # Modern green
            'accent': [0.58, 0.42, 0.95, 1],           # Purple accent
            'border': [0.25, 0.25, 0.28, 1],           # Dark border
        }
    })
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind to theme_mode changes to update UI reactively
        self.bind(theme_mode=self._on_theme_mode_change)
    
    def _on_theme_mode_change(self, *args):
        """Called when theme_mode changes to trigger UI updates."""
        # Force the theme_colors property to notify all bindings in KV file
        # This ensures all app.get_color() calls are re-evaluated
        self.property('theme_colors').dispatch(self)
    
    def get_color(self, color_key):
        """Get color for the current theme."""
        return self.theme_colors[self.theme_mode].get(color_key, [1, 1, 1, 1])
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme_mode = 'dark' if self.theme_mode == 'light' else 'light'
        self.save_settings()
    
    def load_settings(self):
        """Load settings from file."""
        try:
            with open('brain_trainer_settings.json', 'r') as f:
                settings = json.load(f)
                self.voice_enabled = settings.get('voice_enabled', False)
                self.theme_mode = settings.get('theme_mode', 'light')
        except (FileNotFoundError, json.JSONDecodeError):
            # Use defaults
            pass
    
    def save_settings(self):
        """Save settings to file."""
        settings = {
            'voice_enabled': self.voice_enabled,
            'theme_mode': self.theme_mode
        }
        with open('brain_trainer_settings.json', 'w') as f:
            json.dump(settings, f)
    
    def on_voice_enabled(self, instance, value):
        """Called when voice_enabled changes."""
        self.save_settings()
    
    def build(self):
        """Build the application."""
        # Load settings
        self.load_settings()
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(NewTrainScreen(name='new_train'))
        sm.add_widget(TrainingScreen(name='training'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        return sm


if __name__ == '__main__':
    BrainTrainerApp().run()
