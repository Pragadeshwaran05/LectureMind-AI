import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-lecturemind'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
    VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'video')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max upload
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'lecturemind.db')
    
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL') or 'gpt-4o'
    AI_BASE_URL = os.environ.get('AI_BASE_URL')
    ASR_MODEL = os.environ.get('ASR_MODEL') or 'whisper-1'
