document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('file-name');
    const extractBtnContainer = document.getElementById('extractBtnContainer');
    const extractBtn = document.getElementById('extractBtn');

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

    function highlight(e) {
        uploadArea.classList.add('dragover');
    }

    function unhighlight(e) {
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
            if (file.type !== 'application/pdf') {
                alert('Please upload a PDF file.');
                return;
            }
            
            // Validate file size (10 MB)
            if (file.size > 10 * 1024 * 1024) {
                alert('File size exceeds 10 MB limit.');
                return;
            }

            fileNameDisplay.innerHTML = `<i class="fa-solid fa-file-pdf me-2"></i>${file.name}`;
            
            // If using standard form submission, the input.files can't be set from drop easily unless we use DataTransfer
            if (fileInput.files !== files) {
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
            }

            // Show extract button (from prompt specs, left card has extract button)
            extractBtnContainer.classList.remove('d-none');
        }
    }

    if(extractBtn) {
        extractBtn.addEventListener('click', () => {
            if(!fileInput.files.length) {
                alert('Please upload a resume first.');
                return;
            }
            // Simulating extraction 
            extractBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Extracting...';
            extractBtn.disabled = true;
            
            setTimeout(() => {
                extractBtn.innerHTML = '<i class="fa-solid fa-check me-2"></i>Extracted';
                extractBtn.classList.remove('btn-outline-primary');
                extractBtn.classList.add('btn-success');
            }, 1500);
        });
    }
});
