document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // Index Page Logic (File Upload & Sample JDs)
    // ---------------------------------------------------------
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('file-name');
    const extractBtnContainer = document.getElementById('extractBtnContainer');
    const analyzerForm = document.getElementById('analyzerForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Sample JDs Elements
    const samplePythonBtn = document.getElementById('samplePythonBtn');
    const sampleReactBtn = document.getElementById('sampleReactBtn');
    const sampleDataBtn = document.getElementById('sampleDataBtn');
    const jobTitleInput = document.getElementById('jobTitle');
    const jobDescriptionInput = document.getElementById('jobDescription');

    if (uploadArea && fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            uploadArea.classList.add('dragover');
        }

        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }

        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const file = files[0];
                
                // Validate file type
                if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
                    alert('Please upload a PDF file.');
                    return;
                }
                
                // Validate file size (10 MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('File size exceeds 10 MB limit.');
                    return;
                }

                if (fileNameDisplay) {
                    fileNameDisplay.classList.remove('d-none');
                    fileNameDisplay.innerHTML = `<i class="fa-solid fa-file-pdf me-2 text-danger"></i>${file.name} <span class="badge bg-success ms-2">Ready</span>`;
                }
                
                if (fileInput.files !== files) {
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    fileInput.files = dataTransfer.files;
                }

                if (extractBtnContainer) {
                    extractBtnContainer.classList.remove('d-none');
                }
            }
        }
    }

    // ---------------------------------------------------------
    // Quick Fill Sample Job Descriptions
    // ---------------------------------------------------------
    if (samplePythonBtn && jobTitleInput && jobDescriptionInput) {
        samplePythonBtn.addEventListener('click', () => {
            jobTitleInput.value = 'Python Developer';
            jobDescriptionInput.value = 'We are looking for a Python Developer proficient in Django, Flask, FastAPI, SQL, MySQL, PostgreSQL, Docker, AWS, Git, and REST APIs. Experience with Machine Learning, Pandas, and NumPy is a plus.';
        });
    }

    if (sampleReactBtn && jobTitleInput && jobDescriptionInput) {
        sampleReactBtn.addEventListener('click', () => {
            jobTitleInput.value = 'Frontend React Developer';
            jobDescriptionInput.value = 'Seeking a skilled Frontend Developer experienced in JavaScript, TypeScript, React, Next.js, HTML, CSS, Bootstrap, Node.js, Express.js, Git, and GitHub.';
        });
    }

    if (sampleDataBtn && jobTitleInput && jobDescriptionInput) {
        sampleDataBtn.addEventListener('click', () => {
            jobTitleInput.value = 'Data Scientist';
            jobDescriptionInput.value = 'Looking for a Data Scientist skilled in Python, SQL, Machine Learning, Deep Learning, Pandas, NumPy, Matplotlib, Power BI, Tableau, and Scikit-Learn.';
        });
    }

    // ---------------------------------------------------------
    // Form Submit Loading Indicator
    // ---------------------------------------------------------
    if (analyzerForm && analyzeBtn) {
        analyzerForm.addEventListener('submit', (e) => {
            if (analyzerForm.checkValidity()) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Analyzing Resume with AI...`;
            }
        });
    }

    // ---------------------------------------------------------
    // Result Page Logic (Score & Progress Animations)
    // ---------------------------------------------------------
    const scoreCircle = document.querySelector('.score-circle');
    const scoreText = document.getElementById('animated-score');
    
    if (scoreCircle && scoreText) {
        const targetScore = parseInt(scoreCircle.getAttribute('data-score'), 10) || 0;
        let currentScore = 0;
        
        const duration = 1500;
        const intervalTime = 20;
        const steps = duration / intervalTime;
        const increment = targetScore / steps;

        const timer = setInterval(() => {
            currentScore += increment;
            if (currentScore >= targetScore) {
                currentScore = targetScore;
                clearInterval(timer);
            }
            
            scoreText.textContent = Math.round(currentScore) + '%';
            
            const degrees = (currentScore / 100) * 360;
            scoreCircle.style.background = `conic-gradient(var(--primary-color) ${degrees}deg, #e2e8f0 0deg)`;
            
        }, intervalTime);
    }

    const mainProgressBar = document.getElementById('main-progress-bar');
    if (mainProgressBar) {
        setTimeout(() => {
            const targetWidth = mainProgressBar.getAttribute('data-target');
            mainProgressBar.style.width = targetWidth + '%';
        }, 300);
    }

    const scoreBars = document.querySelectorAll('.score-bar');
    if (scoreBars.length > 0) {
        setTimeout(() => {
            scoreBars.forEach(bar => {
                const width = bar.getAttribute('data-width');
                if (width) {
                    bar.style.width = width;
                }
            });
        }, 300);
    }

});
