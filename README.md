# LectureMind AI

**Turn Every Lecture into Intelligent Study Material.**

LectureMind AI is a focused web application that transforms lecture audio/video files into transcripts, intelligent study notes, and AI-generated quizzes.

## Three Core Features

1. **🎙️ Real Speech-to-Text**: Upload an audio or video file (MP3, WAV, M4A, MP4, MOV, MKV), extract the audio (if video), and generate a real transcript using a Whisper-compatible ASR API.
2. **🧠 AI Study Analysis**: Transforms the generated transcript into a concise summary, important topics, key points, and structured student-friendly study notes.
3. **❓ AI Quiz**: Generates a 10-question multiple choice quiz directly from the transcript, with a real scoring system.

## Architecture & Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Video Processing**: FFmpeg (via MoviePy)
- **Speech & AI**: Configurable OpenAI API (compatible with GPT-4 and Whisper)

## Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **FFmpeg**: Required for extracting audio from video files.
   - **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install via winget: `winget install ffmpeg`
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

### Environment Setup

Run these commands from the project root:

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to include your `AI_API_KEY`.*

5. **Run the application**:
   ```bash
   python app.py
   ```
   *The database will be automatically created on the first run.*

## Usage

1. Open `http://localhost:5000` in your web browser.
2. **Upload**: Click "Analyze My Lecture" and upload a valid media file.
3. **Transcript**: Wait for the processing to finish. You can view, copy, or download the generated transcript.
4. **Analysis**: Click "Continue to AI Analysis" to generate the study material.
5. **Quiz**: Click "Generate AI Quiz" to take a quiz based on the lecture. Submit your answers to see your score and explanations.

## Troubleshooting

- **FFmpeg Error**: Ensure FFmpeg is installed and added to your system's PATH.
- **API Error**: Ensure your `.env` contains a valid API key with sufficient credits.
- **Large Files**: Processing large files may take time depending on the API speed.
