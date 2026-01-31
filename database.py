"""Database module for brain training app."""
import sqlite3
import os
from datetime import datetime


class Database:
    """Manages SQLite database for training statistics."""
    
    def __init__(self, db_path='brain_trainer.db'):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create training sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                difficulty TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                time_per_question INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_training_session(self, difficulty, total_questions, correct_answers, time_per_question):
        """Add a new training session record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_sessions 
            (difficulty, total_questions, correct_answers, time_per_question, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (difficulty, total_questions, correct_answers, time_per_question, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """Get overall statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                SUM(total_questions) as total_questions,
                SUM(correct_answers) as correct_answers
            FROM training_sessions
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_sessions': result[0] or 0,
            'total_questions': result[1] or 0,
            'correct_answers': result[2] or 0,
            'accuracy': (result[2] / result[1] * 100) if result[1] else 0
        }
    
    def get_recent_sessions(self, limit=5):
        """Get recent training sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT difficulty, total_questions, correct_answers, date
            FROM training_sessions
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
