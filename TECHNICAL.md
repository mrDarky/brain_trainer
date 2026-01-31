# Brain Trainer App - Technical Documentation

## Project Structure

```
brain_trainer/
├── main.py              # Main application with Kivy UI logic
├── database.py          # SQLite database management
├── braintrainer.kv      # Kivy UI layouts
├── requirements.txt     # Python dependencies
├── test_app.py          # Validation tests
├── USAGE.py             # Usage guide
├── README.md            # User documentation
└── .gitignore          # Git ignore rules
```

## Architecture

### 1. Database Layer (`database.py`)

**Class: Database**
- `__init__(db_path)`: Initialize database connection
- `init_db()`: Create tables if they don't exist
- `add_training_session()`: Save training results
- `get_statistics()`: Get overall performance stats
- `get_recent_sessions()`: Get recent training history

**Schema:**
```sql
CREATE TABLE training_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    difficulty TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    time_per_question INTEGER NOT NULL,
    date TEXT NOT NULL
)
```

### 2. Application Layer (`main.py`)

**Classes:**

1. **MainScreen (Screen)**
   - Display training statistics
   - Navigate to New Training or Settings
   - Update statistics on screen entry

2. **NewTrainScreen (Screen)**
   - Select difficulty (Easy/Medium/Hard/Custom)
   - Configure time per question
   - Set custom range for Custom difficulty
   - Start training session

3. **TrainingScreen (Screen)**
   - Generate multiplication questions
   - Countdown timer for each question
   - Answer validation
   - Score tracking
   - Result popup with Next/End options
   - Text-to-speech support (if enabled)

4. **SettingsScreen (Screen)**
   - Toggle voice/TTS feature
   - Return to main menu

5. **BrainTrainerApp (App)**
   - Main application class
   - Screen management
   - Global voice_enabled property

### 3. UI Layer (`braintrainer.kv`)

**Screens:**
- MainScreen: Statistics display + navigation buttons
- NewTrainScreen: Difficulty selector + time input + custom range
- TrainingScreen: Question display + timer + answer input
- SettingsScreen: Voice toggle + back button

## Features Implementation

### Difficulty Levels
- **Easy**: Random numbers 0-10
- **Medium**: Random numbers 10-20
- **Hard**: Random numbers 20-100
- **Custom**: User-defined min/max range

### Timer System
- Default: 10 seconds per question
- Custom: User-defined time
- Visual countdown display
- Auto-submit on timeout

### Voice/TTS System
- Uses pyttsx3 library
- Speaks question: "X times Y"
- Configurable in Settings
- Graceful fallback if unavailable

### Statistics Tracking
- Total training sessions
- Total questions answered
- Total correct answers
- Overall accuracy percentage
- Recent session history

## Data Flow

1. **Start Training:**
   - User selects difficulty + time → NewTrainScreen
   - Start button → TrainingScreen.setup_training()
   - Generate first question → Start timer

2. **During Training:**
   - Timer counts down
   - User enters answer
   - Submit → Check answer
   - Show result popup
   - Next question or End training

3. **End Training:**
   - Save to database
   - Return to MainScreen
   - Update statistics

## Testing

Run validation tests:
```bash
python test_app.py
```

Tests cover:
- Database CRUD operations
- Statistics calculations
- Difficulty range configurations
- Multiplication logic
- Timer values

## Dependencies

- **Kivy 2.3.0**: Cross-platform GUI framework
- **pyttsx3 2.90**: Text-to-speech engine (optional)
- **SQLite3**: Built-in Python database (no installation needed)

## Platform Support

- ✓ Windows
- ✓ macOS
- ✓ Linux
- ✓ Android (with Buildozer)
- ✓ iOS (with Kivy-iOS)

## Error Handling

- Graceful TTS initialization failure
- Input validation for time/range values
- Database connection error handling
- Safe exception handling (Exception, not bare except)

## Future Enhancements

Possible improvements:
- Add more operation types (addition, subtraction, division)
- Difficulty progression (adaptive difficulty)
- Multiple user profiles
- Achievements and badges
- Leaderboard
- Sound effects
- Dark mode
- Multiple languages
