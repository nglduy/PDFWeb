// Global variables
let selectedFiles = [];
let currentPdfInfo = null;
let selectedPages = new Set();

// DOM Elements
const mergeTab = document.getElementById('merge');
const splitTab = document.getElementById('split');
const tabButtons = document.querySelectorAll('.tab-button');
const mergeFilesInput = document.getElementById('merge-files');
const mergeUploadArea = document.getElementById('merge-upload-area');
const mergeFileList = document.getElementById('merge-file-list');
const mergeBtn = document.getElementById('merge-btn');
const splitFileInput = document.getElementById('split-file');
const splitUploadArea = document.getElementById('split-upload-area');
const splitFileInfo = document.getElementById('split-file-info');
const pageSelector = document.getElementById('page-selector');
const splitBtn = document.getElementById('split-btn');
const progressOverlay = document.getElementById('progress-overlay');
const progressMessage = document.getElementById('progress-message');
const messageContainer = document.getElementById('message-container');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeMergeFeature();
    initializeSplitFeature();
});

/**
 * Tab Management Functions
 */
function initializeTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update tab buttons
    tabButtons.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // Reset forms when switching tabs
    if (tabName === 'merge') {
        resetMergeForm();
    } else {
        resetSplitForm();
    }
}

/**
 * Merge PDF Functions
 */
function initializeMergeFeature() {
    // File input change handler
    mergeFilesInput.addEventListener('change', handleMergeFileSelect);
    
    // Upload area click handler
    mergeUploadArea.addEventListener('click', () => mergeFilesInput.click());
    
    // Drag and drop handlers
    mergeUploadArea.addEventListener('dragover', handleDragOver);
    mergeUploadArea.addEventListener('dragenter', handleDragEnter);
    mergeUploadArea.addEventListener('dragleave', handleDragLeave);
    mergeUploadArea.addEventListener('drop', handleMergeDrop);
    
    // Merge button handler
    mergeBtn.addEventListener('click', handleMerge);
}

function handleMergeFileSelect(event) {
    const files = Array.from(event.target.files);
    addFilesToMergeList(files);
}

function addFilesToMergeList(files) {
    // Validate files
    const validFiles = files.filter(file => {
        if (file.type !== 'application/pdf') {
            showMessage(`${file.name} is not a PDF file`, 'error');
            return false;
        }
        if (file.size > 50 * 1024 * 1024) { // 50MB
            showMessage(`${file.name} is too large (max 50MB)`, 'error');
            return false;
        }
        return true;
    });

    // Add to selected files
    selectedFiles = [...selectedFiles, ...validFiles];
    updateMergeFileList();
    updateMergeButton();
}

function updateMergeFileList() {
    mergeFileList.innerHTML = '';
    
    if (selectedFiles.length === 0) {
        mergeFileList.innerHTML = '<p style="color: #718096; text-align: center;">No files selected</p>';
        return;
    }

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div>
                <strong>${file.name}</strong>
                <br>
                <small>${formatFileSize(file.size)}</small>
            </div>
            <div>
                <button type="button" onclick="removeFileFromMerge(${index})" class="btn btn-small btn-secondary">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
        `;
        mergeFileList.appendChild(fileItem);
    });
}

function removeFileFromMerge(index) {
    selectedFiles.splice(index, 1);
    updateMergeFileList();
    updateMergeButton();
}

function updateMergeButton() {
    mergeBtn.disabled = selectedFiles.length < 2;
}

function resetMergeForm() {
    selectedFiles = [];
    mergeFilesInput.value = '';
    updateMergeFileList();
    updateMergeButton();
}

async function handleMerge() {
    if (selectedFiles.length < 2) {
        showMessage('Please select at least 2 PDF files', 'error');
        return;
    }

    showProgress('Merging PDFs...');

    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('pdfs', file);
        });

        const response = await fetch('/merge', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to merge PDFs');
        }

        // Download the merged PDF
        const blob = await response.blob();
        downloadFile(blob, 'merged.pdf');
        
        showMessage('PDFs merged successfully!', 'success');
        resetMergeForm();

    } catch (error) {
        console.error('Merge error:', error);
        showMessage(error.message, 'error');
    } finally {
        hideProgress();
    }
}

/**
 * Split PDF Functions
 */
function initializeSplitFeature() {
    // File input change handler
    splitFileInput.addEventListener('change', handleSplitFileSelect);
    
    // Upload area click handler
    splitUploadArea.addEventListener('click', () => splitFileInput.click());
    
    // Drag and drop handlers
    splitUploadArea.addEventListener('dragover', handleDragOver);
    splitUploadArea.addEventListener('dragenter', handleDragEnter);
    splitUploadArea.addEventListener('dragleave', handleDragLeave);
    splitUploadArea.addEventListener('drop', handleSplitDrop);
    
    // Split button handler
    splitBtn.addEventListener('click', handleSplit);
    
    // Page selection method handlers
    document.querySelectorAll('input[name="selection-method"]').forEach(radio => {
        radio.addEventListener('change', handleSelectionMethodChange);
    });
    
    // Range inputs handlers
    document.getElementById('apply-range').addEventListener('click', applyPageRange);
    document.getElementById('clear-selection').addEventListener('click', clearPageSelection);
}

async function handleSplitFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        await processSplitFile(file);
    }
}

async function processSplitFile(file) {
    // Validate file
    if (file.type !== 'application/pdf') {
        showMessage('Please select a PDF file', 'error');
        return;
    }

    if (file.size > 50 * 1024 * 1024) { // 50MB
        showMessage('File too large (max 50MB)', 'error');
        return;
    }

    showProgress('Analyzing PDF...');

    try {
        const formData = new FormData();
        formData.append('pdf', file);

        const response = await fetch('/pdf-info', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to analyze PDF');
        }

        currentPdfInfo = await response.json();
        displayPdfInfo();
        createPageSelector();
        
    } catch (error) {
        console.error('PDF analysis error:', error);
        showMessage(error.message, 'error');
    } finally {
        hideProgress();
    }
}

function displayPdfInfo() {
    document.getElementById('split-filename').textContent = `File: ${currentPdfInfo.originalName}`;
    document.getElementById('split-pages').textContent = `Total pages: ${currentPdfInfo.pageCount}`;
    splitFileInfo.style.display = 'block';
    pageSelector.style.display = 'block';
}

function createPageSelector() {
    const pageCheckboxes = document.getElementById('page-checkboxes');
    const rangeStart = document.getElementById('range-start');
    const rangeEnd = document.getElementById('range-end');
    
    pageCheckboxes.innerHTML = '';
    rangeStart.max = currentPdfInfo.pageCount;
    rangeEnd.max = currentPdfInfo.pageCount;
    
    for (let i = 1; i <= currentPdfInfo.pageCount; i++) {
        const pageDiv = document.createElement('div');
        pageDiv.className = 'page-checkbox';
        pageDiv.textContent = i;
        pageDiv.dataset.page = i;
        pageDiv.addEventListener('click', () => togglePageSelection(i, pageDiv));
        pageCheckboxes.appendChild(pageDiv);
    }
    
    selectedPages.clear();
    updateSelectedPagesDisplay();
    updateSplitButton();
}

function togglePageSelection(pageNumber, element) {
    if (selectedPages.has(pageNumber)) {
        selectedPages.delete(pageNumber);
        element.classList.remove('selected');
    } else {
        selectedPages.add(pageNumber);
        element.classList.add('selected');
    }
    
    updateSelectedPagesDisplay();
    updateSplitButton();
}

function handleSelectionMethodChange(event) {
    const method = event.target.value;
    const rangeInputs = document.querySelector('.range-inputs');
    const pageCheckboxes = document.getElementById('page-checkboxes');
    
    if (method === 'range') {
        rangeInputs.style.display = 'flex';
        pageCheckboxes.style.pointerEvents = 'none';
        pageCheckboxes.style.opacity = '0.5';
    } else {
        rangeInputs.style.display = 'none';
        pageCheckboxes.style.pointerEvents = 'auto';
        pageCheckboxes.style.opacity = '1';
    }
}

function applyPageRange() {
    const start = parseInt(document.getElementById('range-start').value);
    const end = parseInt(document.getElementById('range-end').value);
    
    if (!start || !end || start > end || start < 1 || end > currentPdfInfo.pageCount) {
        showMessage('Please enter a valid page range', 'error');
        return;
    }
    
    // Clear current selection
    selectedPages.clear();
    document.querySelectorAll('.page-checkbox').forEach(el => el.classList.remove('selected'));
    
    // Select range
    for (let i = start; i <= end; i++) {
        selectedPages.add(i);
        const element = document.querySelector(`.page-checkbox[data-page="${i}"]`);
        if (element) element.classList.add('selected');
    }
    
    updateSelectedPagesDisplay();
    updateSplitButton();
    showMessage(`Selected pages ${start} to ${end}`, 'success');
}

function clearPageSelection() {
    selectedPages.clear();
    document.querySelectorAll('.page-checkbox').forEach(el => el.classList.remove('selected'));
    updateSelectedPagesDisplay();
    updateSplitButton();
}

function updateSelectedPagesDisplay() {
    const display = document.getElementById('selected-pages-display');
    if (selectedPages.size === 0) {
        display.textContent = 'None';
    } else {
        const sortedPages = Array.from(selectedPages).sort((a, b) => a - b);
        display.textContent = sortedPages.join(', ');
    }
}

function updateSplitButton() {
    splitBtn.disabled = selectedPages.size === 0;
}

function resetSplitForm() {
    splitFileInput.value = '';
    splitFileInfo.style.display = 'none';
    pageSelector.style.display = 'none';
    currentPdfInfo = null;
    selectedPages.clear();
    updateSplitButton();
    
    // Reset radio buttons
    document.querySelector('input[name="selection-method"][value="individual"]').checked = true;
    handleSelectionMethodChange({ target: { value: 'individual' } });
}

async function handleSplit() {
    if (selectedPages.size === 0) {
        showMessage('Please select at least one page', 'error');
        return;
    }

    showProgress('Splitting PDF...');

    try {
        const response = await fetch('/split', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentPdfInfo.filename,
                pages: Array.from(selectedPages)
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to split PDF');
        }

        // Download the split PDF
        const blob = await response.blob();
        const sortedPages = Array.from(selectedPages).sort((a, b) => a - b);
        const filename = `split_pages_${sortedPages.join('_')}.pdf`;
        downloadFile(blob, filename);
        
        showMessage('PDF split successfully!', 'success');
        resetSplitForm();

    } catch (error) {
        console.error('Split error:', error);
        showMessage(error.message, 'error');
    } finally {
        hideProgress();
    }
}

/**
 * Drag and Drop Functions
 */
function handleDragOver(event) {
    event.preventDefault();
}

function handleDragEnter(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    if (!event.currentTarget.contains(event.relatedTarget)) {
        event.currentTarget.classList.remove('drag-over');
    }
}

function handleMergeDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const files = Array.from(event.dataTransfer.files);
    addFilesToMergeList(files);
}

async function handleSplitDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) {
        await processSplitFile(files[0]);
    }
}

/**
 * Utility Functions
 */
function showProgress(message) {
    progressMessage.textContent = message;
    progressOverlay.style.display = 'flex';
}

function hideProgress() {
    progressOverlay.style.display = 'none';
}

function showMessage(text, type = 'info') {
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    message.addEventListener('click', () => message.remove());
    
    messageContainer.appendChild(message);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 5000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}