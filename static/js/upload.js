document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadBtn');
    
    const processingState = document.getElementById('processingState');
    const progressBar = document.getElementById('progressBar');
    
    let selectedFile = null;

    // Drag and Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'var(--secondary)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = 'white';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'white';
        
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        selectedFile = file;
        fileName.textContent = file.name;
        uploadArea.classList.add('hidden');
        fileInfo.classList.remove('hidden');
    }

    uploadBtn.addEventListener('click', () => {
        if (!selectedFile) return;
        
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        fileInfo.classList.add('hidden');
        processingState.classList.remove('hidden');
        
        updateProgress(10, 1); // Uploading
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            
            updateProgress(40, 2); // Processing audio
            
            // Start processing (extraction/transcription)
            return fetch(`/process/${data.lecture_id}`, { method: 'POST' });
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            
            updateProgress(100, 3);
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 500);
        })
        .catch(error => {
            alert('Error: ' + error.message);
            fileInfo.classList.remove('hidden');
            processingState.classList.add('hidden');
        });
    });
    
    function updateProgress(percent, stepNumber) {
        progressBar.style.width = `${percent}%`;
        
        for (let i = 1; i <= 3; i++) {
            const step = document.getElementById(`step${i}`);
            if (i < stepNumber) {
                step.className = 'completed';
                step.textContent = step.textContent.replace('...', '') + ' ✓';
            } else if (i === stepNumber) {
                step.className = 'active';
            }
        }
    }
});
