from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import io
from datetime import datetime
import tempfile

# Initialize Flask app for Vercel
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB file upload limit
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if uploaded file is a PDF"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(original_name, prefix=""):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(secure_filename(original_name))
    return f"{timestamp}_{prefix}{name}{ext}"

# Global variable to store PDF data temporarily (for serverless)
pdf_cache = {}

@app.route('/')
def index():
    """Serve the main page"""
    # For Vercel, we need to serve static content differently
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Merger & Splitter</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* Inline CSS for Vercel deployment */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; min-height: 100vh; }
        .header { text-align: center; margin-bottom: 30px; color: white; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .tabs { display: flex; gap: 10px; margin-bottom: 30px; justify-content: center; }
        .tab-button {
            background: rgba(255,255,255,0.2); color: white;
            border: 2px solid rgba(255,255,255,0.3); padding: 15px 30px;
            border-radius: 10px; cursor: pointer; font-size: 1rem; font-weight: 600;
            transition: all 0.3s ease; backdrop-filter: blur(10px);
        }
        .tab-button:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
        .tab-button.active { background: white; color: #667eea; border-color: white; }
        .tab-content { display: none; animation: fadeIn 0.5s ease; }
        .tab-content.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .section {
            background: white; border-radius: 20px; padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); backdrop-filter: blur(10px);
        }
        .section h2 { color: #4a5568; margin-bottom: 10px; font-size: 1.8rem; }
        .section p { color: #718096; margin-bottom: 25px; }
        .upload-area {
            border: 3px dashed #e2e8f0; border-radius: 15px; padding: 40px 20px;
            text-align: center; transition: all 0.3s ease; cursor: pointer; margin-bottom: 20px;
        }
        .upload-area:hover { border-color: #667eea; background: rgba(102, 126, 234, 0.05); }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
            border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer;
            font-size: 1rem; font-weight: 600; transition: all 0.3s ease;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        .btn:disabled { background: #cbd5e0; cursor: not-allowed; transform: none; box-shadow: none; }
        .file-list { margin: 20px 0; }
        .file-item {
            background: #f7fafc; padding: 15px; border-radius: 10px;
            margin-bottom: 10px; border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-file-pdf"></i> PDF Tools</h1>
            <p>Merge multiple PDFs or split a single PDF into pages</p>
        </header>

        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('merge')">
                <i class="fas fa-compress-arrows-alt"></i> Merge PDFs
            </button>
            <button class="tab-button" onclick="switchTab('split')">
                <i class="fas fa-expand-arrows-alt"></i> Split PDF
            </button>
        </div>

        <div id="merge" class="tab-content active">
            <div class="section">
                <h2>Merge Multiple PDFs</h2>
                <p>Select multiple PDF files to combine them into one document.</p>
                
                <div class="upload-area" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" style="display: none;">
                    <i class="fas fa-cloud-upload-alt" style="font-size: 3rem; color: #a0aec0; margin-bottom: 15px;"></i>
                    <p>Click to select PDF files</p>
                </div>

                <div id="merge-file-list" class="file-list"></div>
                <button id="merge-btn" class="btn" onclick="mergePDFs()" disabled>
                    <i class="fas fa-compress-arrows-alt"></i> Merge PDFs
                </button>
            </div>
        </div>

        <div id="split" class="tab-content">
            <div class="section">
                <h2>Split PDF into Pages</h2>
                <p>Upload a PDF and select specific pages to extract.</p>
                
                <div class="upload-area" onclick="document.getElementById('split-file').click()">
                    <input type="file" id="split-file" accept=".pdf" style="display: none;">
                    <i class="fas fa-file-upload" style="font-size: 3rem; color: #a0aec0; margin-bottom: 15px;"></i>
                    <p>Click to select a PDF file</p>
                </div>

                <div id="split-info" style="display: none;">
                    <h3>PDF Information</h3>
                    <p id="split-filename"></p>
                    <p id="split-pages"></p>
                    <div style="margin: 20px 0;">
                        <label>Select pages: </label>
                        <input type="text" id="page-numbers" placeholder="e.g., 1,3,5-8" style="padding: 8px; margin: 0 10px;">
                        <button class="btn" onclick="splitPDF()">Split PDF</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFiles = [];
        let currentPdfInfo = null;

        function switchTab(tabName) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        document.getElementById('merge-files').addEventListener('change', function(e) {
            selectedFiles = Array.from(e.target.files);
            updateFileList();
        });

        document.getElementById('split-file').addEventListener('change', function(e) {
            if (e.target.files[0]) {
                analyzePDF(e.target.files[0]);
            }
        });

        function updateFileList() {
            const list = document.getElementById('merge-file-list');
            list.innerHTML = '';
            
            selectedFiles.forEach((file, index) => {
                const item = document.createElement('div');
                item.className = 'file-item';
                item.innerHTML = `
                    <strong>${file.name}</strong>
                    <button onclick="removeFile(${index})" style="float: right; background: #f56565; color: white; border: none; padding: 5px 10px; border-radius: 5px;">Remove</button>
                `;
                list.appendChild(item);
            });
            
            document.getElementById('merge-btn').disabled = selectedFiles.length < 2;
        }

        function removeFile(index) {
            selectedFiles.splice(index, 1);
            updateFileList();
        }

        async function mergePDFs() {
            if (selectedFiles.length < 2) return;
            
            const formData = new FormData();
            selectedFiles.forEach(file => formData.append('pdfs', file));
            
            try {
                const response = await fetch('/api/merge', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, 'merged.pdf');
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        async function analyzePDF(file) {
            const formData = new FormData();
            formData.append('pdf', file);
            
            try {
                const response = await fetch('/api/pdf-info', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    currentPdfInfo = await response.json();
                    document.getElementById('split-filename').textContent = `File: ${currentPdfInfo.originalName}`;
                    document.getElementById('split-pages').textContent = `Total pages: ${currentPdfInfo.pageCount}`;
                    document.getElementById('split-info').style.display = 'block';
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        async function splitPDF() {
            if (!currentPdfInfo) return;
            
            const pageInput = document.getElementById('page-numbers').value;
            const pages = parsePageNumbers(pageInput);
            
            if (pages.length === 0) {
                alert('Please enter valid page numbers');
                return;
            }
            
            try {
                const response = await fetch('/api/split', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        filename: currentPdfInfo.filename,
                        pages: pages
                    })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, `split_pages_${pages.join('_')}.pdf`);
                } else {
                    const error = await response.json();
                    alert('Error: ' + error.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        function parsePageNumbers(input) {
            const pages = [];
            const parts = input.split(',');
            
            parts.forEach(part => {
                part = part.trim();
                if (part.includes('-')) {
                    const [start, end] = part.split('-').map(n => parseInt(n.trim()));
                    for (let i = start; i <= end; i++) {
                        pages.push(i);
                    }
                } else {
                    const num = parseInt(part);
                    if (!isNaN(num)) pages.push(num);
                }
            });
            
            return [...new Set(pages)].sort((a, b) => a - b);
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
    </script>
</body>
</html>"""
    return html_content

@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    """Merge multiple PDF files into one"""
    try:
        if 'pdfs' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('pdfs')
        
        if len(files) < 2:
            return jsonify({'error': 'At least 2 PDF files are required'}), 400
        
        pdf_writer = PdfWriter()
        
        for file in files:
            if file and allowed_file(file.filename):
                file_bytes = file.read()
                pdf_reader = PdfReader(io.BytesIO(file_bytes))
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
            else:
                return jsonify({'error': f'Invalid file: {file.filename}'}), 400
        
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to merge PDFs: {str(e)}'}), 500

@app.route('/api/pdf-info', methods=['POST'])
def get_pdf_info():
    """Get information about uploaded PDF"""
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file uploaded'}), 400
        
        file = request.files['pdf']
        
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        file_bytes = file.read()
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(pdf_reader.pages)
        
        cache_key = generate_filename(file.filename, "cache_")
        pdf_cache[cache_key] = file_bytes
        
        return jsonify({
            'pageCount': page_count,
            'filename': cache_key,
            'originalName': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to read PDF: {str(e)}'}), 500

@app.route('/api/split', methods=['POST'])
def split_pdf():
    """Split PDF by extracting specific pages"""
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data or 'pages' not in data:
            return jsonify({'error': 'Invalid request'}), 400
        
        filename = data['filename']
        pages = data['pages']
        
        if filename not in pdf_cache:
            return jsonify({'error': 'PDF file not found'}), 404
        
        file_bytes = pdf_cache[filename]
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(pdf_reader.pages)
        
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            return jsonify({'error': f'Invalid pages: {invalid_pages}'}), 400
        
        pdf_writer = PdfWriter()
        
        for page_num in sorted(pages):
            page_index = page_num - 1
            page = pdf_reader.pages[page_index]
            pdf_writer.add_page(page)
        
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        # Clean up cache
        del pdf_cache[filename]
        
        download_name = f"split_pages_{'_'.join(map(str, sorted(pages)))}.pdf"
        
        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to split PDF: {str(e)}'}), 500

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)