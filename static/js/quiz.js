document.addEventListener('DOMContentLoaded', function() {
    let currentQuestionIndex = 0;
    const questions = document.querySelectorAll('.question-card');
    const total = questions.length;
    const userAnswers = {};
    
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const currentNumSpan = document.getElementById('currentQuestionNum');
    
    // Add event listeners to radio buttons to record answers
    questions.forEach(q => {
        const radios = q.querySelectorAll('input[type="radio"]');
        radios.forEach(r => {
            r.addEventListener('change', (e) => {
                const qId = q.getAttribute('data-id');
                userAnswers[qId] = e.target.value;
            });
        });
    });
    
    prevBtn.addEventListener('click', () => {
        if (currentQuestionIndex > 0) {
            questions[currentQuestionIndex].classList.add('hidden');
            questions[currentQuestionIndex].classList.remove('active');
            
            currentQuestionIndex--;
            
            questions[currentQuestionIndex].classList.remove('hidden');
            questions[currentQuestionIndex].classList.add('active');
            
            updateButtons();
        }
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentQuestionIndex < total - 1) {
            questions[currentQuestionIndex].classList.add('hidden');
            questions[currentQuestionIndex].classList.remove('active');
            
            currentQuestionIndex++;
            
            questions[currentQuestionIndex].classList.remove('hidden');
            questions[currentQuestionIndex].classList.add('active');
            
            updateButtons();
        }
    });
    
    submitBtn.addEventListener('click', () => {
        // Validate all answered
        if (Object.keys(userAnswers).length < total) {
            if (!confirm('You have not answered all questions. Submit anyway?')) {
                return;
            }
        }
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        fetch(`/lecture/${lectureId}/quiz/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers: userAnswers })
        })
        .then(res => res.json())
        .then(data => {
            showResults(data);
        })
        .catch(err => {
            alert('Error submitting quiz');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Quiz';
        });
    });
    
    function updateButtons() {
        currentNumSpan.textContent = currentQuestionIndex + 1;
        
        prevBtn.disabled = currentQuestionIndex === 0;
        
        if (currentQuestionIndex === total - 1) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }
    
    function showResults(data) {
        document.getElementById('quizContainer').classList.add('hidden');
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.classList.remove('hidden');
        
        document.getElementById('finalScore').textContent = `${data.score} / ${data.total}`;
        document.getElementById('finalPercentage').textContent = `${Math.round(data.percentage)}%`;
        
        document.getElementById('correctCount').textContent = data.score;
        document.getElementById('incorrectCount').textContent = data.total - data.score;
        
        const detailedResults = document.getElementById('detailedResults');
        let html = '';
        
        data.results.forEach((r, idx) => {
            const isCorrect = r.is_correct;
            const cls = isCorrect ? 'correct-item' : 'incorrect-item';
            
            html += `
                <div class="result-item ${cls}">
                    <h4>Q${idx + 1}. ${r.question}</h4>
                    <div class="answer-comparison">
                        <p><strong>Your answer:</strong> ${r.student_answer || 'Skipped'} 
                           ${isCorrect ? '✅' : '❌'}</p>
                        ${!isCorrect ? `<p><strong>Correct answer:</strong> ${r.correct_answer}</p>` : ''}
                    </div>
                    <p class="explanation">${r.explanation}</p>
                </div>
            `;
        });
        
        detailedResults.innerHTML = html;
    }
});
