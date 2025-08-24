// Global variables
let selectedFile = null;
let analysisResults = null;

// DOM elements - will be initialized after DOM loads
let dropZone, fileInput, dragIndicator, jobDescription, targetRole, industry, experienceLevel, analyzeBtn, resultsSection, loadingState, analysisResults;

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, setting up application...');
    
    // Initialize DOM elements
    dropZone = document.getElementById('dropZone');
    fileInput = document.getElementById('fileInput');
    dragIndicator = document.getElementById('dragIndicator');
    jobDescription = document.getElementById('jobDescription');
    targetRole = document.getElementById('targetRole');
    industry = document.getElementById('industry');
    experienceLevel = document.getElementById('experienceLevel');
    analyzeBtn = document.getElementById('analyzeBtn');
    resultsSection = document.getElementById('resultsSection');
    loadingState = document.getElementById('loadingState');
    analysisResults = document.getElementById('analysisResults');
    
    // Check if all required elements exist
    if (!dropZone) console.error('Drop zone not found!');
    if (!fileInput) console.error('File input not found!');
    if (!dragIndicator) console.error('Drag indicator not found!');
    if (!jobDescription) console.error('Job description not found!');
    if (!analyzeBtn) console.error('Analyze button not found!');
    
    setupEventListeners();
    updateAnalyzeButton();
    console.log('Application setup complete');
});

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Set up drag and drop FIRST, before anything else
    setupDragAndDrop();
    
    // File upload events
    dropZone.addEventListener('click', () => {
        console.log('Drop zone clicked');
        fileInput.click();
    });
    
    fileInput.addEventListener('change', handleFileSelect);

    // Form validation
    jobDescription.addEventListener('input', updateAnalyzeButton);
    fileInput.addEventListener('change', updateAnalyzeButton);

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeResume);

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', switchTab);
    });

    // Download button
    document.getElementById('downloadBtn').addEventListener('click', downloadTailoredResume);
    

    
    console.log('Event listeners set up successfully');
}

function setupDragAndDrop() {
    console.log('Setting up drag and drop...');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
        dragIndicator.classList.remove('hidden');
        console.log('Highlight');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
        dragIndicator.classList.add('hidden');
        console.log('Unhighlight');
    }

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        console.log('Drop detected');
        console.log('Files:', files.length);
        
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }
    
    console.log('Drag and drop setup complete');
}

// File handling functions
// (Drag and drop functions are now defined inline in setupEventListeners)

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Make handleFile globally available
window.handleFile = function(file) {
    console.log('Handling file:', file.name, 'Size:', file.size, 'Type:', file.type);
    
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    console.log('File extension:', fileExtension);
    
    if (!allowedTypes.includes(fileExtension)) {
        showError('Please select a PDF, DOCX, or TXT file.');
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB.');
        return;
    }

    selectedFile = file;
    updateDropZoneText(file.name);
    updateAnalyzeButton();
    console.log('File selected successfully:', file.name);
}

// Make updateDropZoneText globally available
window.updateDropZoneText = function(fileName) {
    dropZone.innerHTML = `
        <i class="fas fa-file-alt text-4xl text-green-500 mb-4"></i>
        <p class="text-lg text-gray-600 mb-2">${fileName}</p>
        <p class="text-sm text-gray-500">Click to change file</p>
    `;
}

// Make updateAnalyzeButton globally available
window.updateAnalyzeButton = function() {
    const hasFile = selectedFile !== null;
    const hasJobDescription = jobDescription.value.trim().length > 0;
    
    analyzeBtn.disabled = !(hasFile && hasJobDescription);
    
    if (analyzeBtn.disabled) {
        analyzeBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        analyzeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// API functions
async function analyzeResume() {
    if (!selectedFile || !jobDescription.value.trim()) {
        showError('Please select a file and enter a job description.');
        return;
    }

    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('resume_file', selectedFile);
        formData.append('job_description', jobDescription.value.trim());
        
        if (targetRole.value.trim()) {
            formData.append('target_role', targetRole.value.trim());
        }
        if (industry.value.trim()) {
            formData.append('industry', industry.value.trim());
        }
        if (experienceLevel.value) {
            formData.append('experience_level', experienceLevel.value);
        }

        const response = await fetch('/resume/analyze-file', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        showResults(result);
        
    } catch (error) {
        console.error('Error analyzing resume:', error);
        showError('An error occurred while analyzing your resume. Please try again.');
        hideLoading();
    }
}

// UI functions
function showLoading() {
    resultsSection.classList.remove('hidden');
    loadingState.classList.remove('hidden');
    analysisResults.classList.add('hidden');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function hideLoading() {
    loadingState.classList.add('hidden');
}

function showResults(data) {
    hideLoading();
    analysisResults.classList.remove('hidden');
    
    // Store results globally
    window.analysisResults = data;
    
    // Update summary
    document.getElementById('confidenceScore').textContent = `${(data.confidence_score * 100).toFixed(1)}%`;
    document.getElementById('keywordsFound').textContent = Object.keys(data.keyword_matches).length;
    document.getElementById('missingKeywords').textContent = data.missing_keywords.length;
    document.getElementById('suggestionsCount').textContent = data.suggestions.length;
    
    // Update tailored resume
    document.getElementById('tailoredResume').textContent = data.tailored_resume;
    
    // Update keywords
    updateKeywordsDisplay(data.keyword_matches, data.missing_keywords);
    
    // Update suggestions
    updateSuggestionsDisplay(data.suggestions);
}

function updateKeywordsDisplay(foundKeywords, missingKeywords) {
    const foundContainer = document.getElementById('foundKeywords');
    const missingContainer = document.getElementById('missingKeywordsList');
    
    // Clear containers
    foundContainer.innerHTML = '';
    missingContainer.innerHTML = '';
    
    // Add found keywords
    Object.entries(foundKeywords).forEach(([keyword, frequency]) => {
        const keywordElement = document.createElement('div');
        keywordElement.className = 'flex items-center justify-between p-2 bg-green-50 rounded';
        keywordElement.innerHTML = `
            <span class="text-green-800 font-medium">${keyword}</span>
            <span class="text-green-600 text-sm">${frequency}×</span>
        `;
        foundContainer.appendChild(keywordElement);
    });
    
    // Add missing keywords
    missingKeywords.forEach(keyword => {
        const keywordElement = document.createElement('div');
        keywordElement.className = 'flex items-center p-2 bg-red-50 rounded';
        keywordElement.innerHTML = `
            <span class="text-red-800 font-medium">${keyword}</span>
            <i class="fas fa-exclamation-triangle text-red-500 ml-2"></i>
        `;
        missingContainer.appendChild(keywordElement);
    });
}

function updateSuggestionsDisplay(suggestions) {
    const container = document.getElementById('suggestionsList');
    container.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const suggestionElement = document.createElement('div');
        suggestionElement.className = 'flex items-start space-x-3 p-4 bg-blue-50 rounded-lg';
        suggestionElement.innerHTML = `
            <div class="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                ${index + 1}
            </div>
            <p class="text-blue-800">${suggestion}</p>
        `;
        container.appendChild(suggestionElement);
    });
}

function switchTab(e) {
    const targetTab = e.target.dataset.tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active', 'border-blue-500', 'text-blue-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    e.target.classList.add('active', 'border-blue-500', 'text-blue-600');
    e.target.classList.remove('border-transparent', 'text-gray-500');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(targetTab + 'Tab').classList.remove('hidden');
}

function downloadTailoredResume() {
    if (!window.analysisResults) return;
    
    const content = window.analysisResults.tailored_resume;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'tailored_resume.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Make showError globally available
window.showError = function(message) {
    // Create error notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
