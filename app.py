import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from config import Config
from database.init_db import get_db_connection, init_db
from utils.file_utils import save_uploaded_file, extract_audio_from_video
from services.speech_to_text import transcribe_audio
from services.ai_service import analyze_transcript
from services.quiz_service import generate_quiz
from io import BytesIO

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folders exist
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        try:
            file_id, file_path, file_type = save_uploaded_file(file)
            if not file_id:
                return jsonify({'error': 'Invalid file type'}), 400
                
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO lectures (id, title, filename, file_type, file_path, status) VALUES (?, ?, ?, ?, ?, ?)',
                (file_id, file.filename, file.filename, file_type, file_path, 'uploaded')
            )
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'lecture_id': file_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return render_template('upload.html')

@app.route('/process/<lecture_id>', methods=['POST'])
def process(lecture_id):
    conn = get_db_connection()
    lecture = conn.execute('SELECT * FROM lectures WHERE id = ?', (lecture_id,)).fetchone()
    
    if not lecture:
        conn.close()
        return jsonify({'error': 'Lecture not found'}), 404
        
    try:
        audio_path = lecture['file_path']
        
        if lecture['file_type'] == 'video':
            conn.execute('UPDATE lectures SET status = ? WHERE id = ?', ('extracting_audio', lecture_id))
            conn.commit()
            audio_path = extract_audio_from_video(lecture['file_path'])
            if not audio_path:
                raise Exception("Failed to extract audio from video")
                
        conn.execute('UPDATE lectures SET status = ? WHERE id = ?', ('transcribing', lecture_id))
        conn.commit()
        
        transcript_text = transcribe_audio(audio_path)
        
        conn.execute(
            'INSERT INTO transcripts (lecture_id, content) VALUES (?, ?)',
            (lecture_id, transcript_text)
        )
        conn.execute('UPDATE lectures SET status = ? WHERE id = ?', ('completed', lecture_id))
        conn.commit()
        
        return jsonify({'success': True, 'redirect_url': url_for('transcript', lecture_id=lecture_id)})
        
    except Exception as e:
        conn.execute('UPDATE lectures SET status = ? WHERE id = ?', ('failed', lecture_id))
        conn.commit()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/lecture/<lecture_id>/transcript')
def transcript(lecture_id):
    conn = get_db_connection()
    lecture = conn.execute('SELECT * FROM lectures WHERE id = ?', (lecture_id,)).fetchone()
    transcript_record = conn.execute('SELECT * FROM transcripts WHERE lecture_id = ?', (lecture_id,)).fetchone()
    conn.close()
    
    if not lecture or not transcript_record:
        return "Transcript not found", 404
        
    return render_template('transcript.html', lecture=lecture, transcript=transcript_record['content'])

@app.route('/lecture/<lecture_id>/download-transcript')
def download_transcript(lecture_id):
    conn = get_db_connection()
    transcript_record = conn.execute('SELECT * FROM transcripts WHERE lecture_id = ?', (lecture_id,)).fetchone()
    conn.close()
    
    if not transcript_record:
        return "Transcript not found", 404
        
    buffer = BytesIO()
    buffer.write(transcript_record['content'].encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'transcript_{lecture_id}.txt',
        mimetype='text/plain'
    )

@app.route('/lecture/<lecture_id>/analysis')
def analysis(lecture_id):
    conn = get_db_connection()
    lecture = conn.execute('SELECT * FROM lectures WHERE id = ?', (lecture_id,)).fetchone()
    analysis_record = conn.execute('SELECT * FROM analyses WHERE lecture_id = ?', (lecture_id,)).fetchone()
    
    if not analysis_record:
        transcript_record = conn.execute('SELECT * FROM transcripts WHERE lecture_id = ?', (lecture_id,)).fetchone()
        if not transcript_record:
            conn.close()
            return "Transcript not found", 404
            
        try:
            result = analyze_transcript(transcript_record['content'])
            conn.execute(
                'INSERT INTO analyses (lecture_id, summary, topics, key_points, study_notes) VALUES (?, ?, ?, ?, ?)',
                (lecture_id, result.get('summary', ''), str(result.get('topics', [])), str(result.get('key_points', [])), result.get('study_notes', ''))
            )
            conn.commit()
            analysis_record = conn.execute('SELECT * FROM analyses WHERE lecture_id = ?', (lecture_id,)).fetchone()
        except Exception as e:
            conn.close()
            return render_template('error.html', message=f"Analysis failed: {str(e)}")
            
    conn.close()
    
    # parse topics and key points since they were stored as string representation of list
    import ast
    topics = ast.literal_eval(analysis_record['topics']) if analysis_record['topics'] else []
    key_points = ast.literal_eval(analysis_record['key_points']) if analysis_record['key_points'] else []
    
    return render_template('analysis.html', lecture=lecture, analysis=analysis_record, topics=topics, key_points=key_points)

@app.route('/lecture/<lecture_id>/quiz')
def quiz(lecture_id):
    conn = get_db_connection()
    lecture = conn.execute('SELECT * FROM lectures WHERE id = ?', (lecture_id,)).fetchone()
    questions = conn.execute('SELECT * FROM quiz_questions WHERE lecture_id = ?', (lecture_id,)).fetchall()
    
    if not questions:
        transcript_record = conn.execute('SELECT * FROM transcripts WHERE lecture_id = ?', (lecture_id,)).fetchone()
        if not transcript_record:
            conn.close()
            return "Transcript not found", 404
            
        try:
            quiz_data = generate_quiz(transcript_record['content'])
            for q in quiz_data.get('questions', []):
                conn.execute(
                    '''INSERT INTO quiz_questions (lecture_id, question, option_a, option_b, option_c, option_d, correct_answer, explanation) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (lecture_id, q['question'], q['options']['A'], q['options']['B'], q['options']['C'], q['options']['D'], q['correct_answer'], q['explanation'])
                )
            conn.commit()
            questions = conn.execute('SELECT * FROM quiz_questions WHERE lecture_id = ?', (lecture_id,)).fetchall()
        except Exception as e:
            conn.close()
            return render_template('error.html', message=f"Quiz generation failed: {str(e)}")
            
    conn.close()
    return render_template('quiz.html', lecture=lecture, questions=questions)

@app.route('/lecture/<lecture_id>/quiz/submit', methods=['POST'])
def submit_quiz(lecture_id):
    data = request.json
    answers = data.get('answers', {})
    
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM quiz_questions WHERE lecture_id = ?', (lecture_id,)).fetchall()
    
    score = 0
    total = len(questions)
    results = []
    
    for q in questions:
        q_id = str(q['id'])
        user_answer = answers.get(q_id)
        is_correct = user_answer == q['correct_answer']
        if is_correct:
            score += 1
            
        results.append({
            'question': q['question'],
            'student_answer': user_answer,
            'correct_answer': q['correct_answer'],
            'explanation': q['explanation'],
            'is_correct': is_correct
        })
        
    percentage = (score / total * 100) if total > 0 else 0
    
    conn.execute(
        'INSERT INTO quiz_results (lecture_id, score, total_questions, percentage) VALUES (?, ?, ?, ?)',
        (lecture_id, score, total, percentage)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'score': score,
        'total': total,
        'percentage': percentage,
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True)
