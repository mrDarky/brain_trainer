"""
Brain Trainer Application - Usage Guide
========================================

APPLICATION STRUCTURE:
---------------------

1. Main Menu (MainScreen)
   - Displays training statistics
   - Total sessions, questions, correct answers, accuracy
   - Navigation to New Training and Settings

2. New Training (NewTrainScreen)
   - Difficulty Selection: Easy, Medium, Hard, Custom
   - Time Configuration: Default 10 seconds or custom
   - Custom Range: Min and Max values for custom difficulty
   - Start Training button

3. Training Session (TrainingScreen)
   - Question Display: Shows multiplication problem
   - Timer: Countdown for each question
   - Score Tracker: Current score (correct/total)
   - Answer Input: Text field for user's answer
   - Submit and End Training buttons
   - Result Popup: Shows if answer was correct/wrong
   - Next Question or End Training options

4. Settings (SettingsScreen)
   - Voice Enable/Disable: Toggle text-to-speech
   - Back to Main Menu button

DIFFICULTY LEVELS:
-----------------
- Easy: Numbers 0-10
- Medium: Numbers 10-20
- Hard: Numbers 20-100
- Custom: User-defined range

DATABASE:
---------
- SQLite database: brain_trainer.db
- Stores: difficulty, total questions, correct answers, time per question, date

FEATURES:
---------
- Automatic timer countdown
- Answer validation
- Statistics tracking
- Text-to-speech support (optional)
- Cross-platform (Windows, macOS, Linux, Android, iOS)

HOW TO RUN:
-----------
1. Install dependencies: pip install -r requirements.txt
2. Run the app: python main.py

NAVIGATION FLOW:
---------------
Main Menu → New Training → Training Session → Results → Main Menu
           ↓
        Settings → Main Menu
"""
