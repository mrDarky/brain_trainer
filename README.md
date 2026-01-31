# Brain Trainer

A multiplatform brain training application built with Python, SQLite, and Kivy.

## Features

- **Multiple Difficulty Levels**: Easy (0-10), Medium (10-20), Hard (20-100), and Custom ranges
- **Statistics Tracking**: View your training history and accuracy
- **Customizable Timer**: Set time per question (default 10 seconds)
- **Voice Support**: Optional text-to-speech to read questions aloud
- **Cross-platform**: Works on Windows, macOS, Linux, Android, and iOS

## Training Modes

- **Easy**: Numbers from 0 to 10
- **Medium**: Numbers from 10 to 20
- **Hard**: Numbers from 20 to 100
- **Custom**: Define your own range

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mrDarky/brain_trainer.git
cd brain_trainer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Navigation

- **Main Menu**: View your training statistics
- **New Training**: Select difficulty, time, and start a training session
- **Settings**: Enable/disable voice features

### Training

1. Select your preferred difficulty level
2. Set the time per question (or use default 10 seconds)
3. For custom mode, enter your own min/max range
4. Answer multiplication questions before time runs out
5. View your results and continue or end the session

## Requirements

- Python 3.7+
- Kivy 2.3.0
- pyttsx3 2.90 (for voice support)

## Database

The app uses SQLite to store training statistics locally in `brain_trainer.db`.

## License

MIT License