import os
import uuid
from werkzeug.utils import secure_filename
from moviepy import VideoFileClip
from config import Config

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'mkv'}
ALLOWED_EXTENSIONS = ALLOWED_AUDIO_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def save_uploaded_file(file):
    if not file or not allowed_file(file.filename):
        return None, None, None

    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{file_id}.{ext}"

    if is_video(filename):
        file_path = os.path.join(Config.VIDEO_FOLDER, new_filename)
        file_type = 'video'
    else:
        file_path = os.path.join(Config.AUDIO_FOLDER, new_filename)
        file_type = 'audio'

    file.save(file_path)
    return file_id, file_path, file_type

def extract_audio_from_video(video_path):
    try:
        audio_filename = os.path.basename(video_path).rsplit('.', 1)[0] + '.mp3'
        audio_path = os.path.join(Config.AUDIO_FOLDER, audio_filename)
        
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def split_audio(audio_path, chunk_length_ms=10 * 60 * 1000): # 10 minutes chunks
    # Not using pydub chunking strictly for now as Whisper can handle quite a bit, 
    # but we can implement basic chunking if file is huge.
    # For now returning the original file. 
    return [audio_path]
