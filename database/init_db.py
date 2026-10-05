import sqlite3
import os
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # LECTURES
    c.execute('''
        CREATE TABLE IF NOT EXISTS lectures (
            id TEXT PRIMARY KEY,
            title TEXT,
            filename TEXT,
            file_type TEXT,
            file_path TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # TRANSCRIPTS
    c.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lecture_id) REFERENCES lectures (id)
        )
    ''')
    
    # ANALYSES
    c.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id TEXT,
            summary TEXT,
            topics TEXT,
            key_points TEXT,
            study_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lecture_id) REFERENCES lectures (id)
        )
    ''')
    
    # QUIZ_QUESTIONS
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id TEXT,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT,
            explanation TEXT,
            FOREIGN KEY (lecture_id) REFERENCES lectures (id)
        )
    ''')
    
    # QUIZ_RESULTS
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id TEXT,
            score INTEGER,
            total_questions INTEGER,
            percentage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lecture_id) REFERENCES lectures (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Create DB on run
    if not os.path.exists(os.path.dirname(Config.DATABASE)):
        os.makedirs(os.path.dirname(Config.DATABASE))
    init_db()
    print("Database initialized.")
