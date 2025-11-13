from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import base64
import uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Simple in-memory cache for this serverless function
pdf_cache = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def generate_filename(original_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}_{original_name}"

@app.route('/')
def home():
    """Serve the main HTML interface"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PDF Tools - Free Online PDF Merger & Splitter</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        h1 { 
            text-align: center; 
            color: #2c3e50; 
            margin-bottom: 10px; 
            font-size: 2.5rem;
        }
        .section { 
            background: #f8f9fa; 
            padding: 30px; 
            margin: 30px 0; 
            border-radius: 15px; 
            border-left: 5px solid #007bff; 
        }
        .btn { 
            background: #007bff;
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .btn:disabled { 
            background: #6c757d; 
            cursor: not-allowed; 
        }
        input[type="file"] { 
            width: 100%; 
            padding: 15px; 
            border: 2px dashed #007bff;
            border-radius: 8px;
            margin: 15px 0;
        }
        input[type="text"] { 
            padding: 15px; 
            border: 2px solid #dee2e6; 
            border-radius: 8px; 
            width: 100%; 
            margin: 15px 0; 
        }
        .status { 
            margin: 20px 0; 
            font-weight: 600; 
            padding: 15px; 
            border-radius: 8px; 
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb; 
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb; 
        }
        .loading { 
            background: #d1ecf1; 
            color: #0c5460; 
        }
        .file-info { 
            background: #e3f2fd;
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 PDF Tools</h1>
        
        <div class="section">
            <h2>📄 Merge PDFs</h2>
            <input type="file" id="mergeFiles" multiple accept=".pdf" onchange="updateFileList()">
            <div id="fileList"></div>
            <button class="btn" id="mergeBtn" onclick="mergePDFs()" disabled>
                🔄 Merge PDFs
            </button>
            <div id="mergeStatus"></div>
        </div>
        
        <div class="section">
            <h2>✂️ Split PDF</h2>
            <input type="file" id="splitFile" accept=".pdf" onchange="analyzePDF()">
            <div id="pdfInfo" style="display:none;">
                <div class="file-info">
                    <p id="pageCount"></p>
                    <p id="fileName"></p>
                </div>
                <input type="text" id="pageNumbers" placeholder="Enter pages (e.g., 1,3,5-8)" />
                <button class="btn" onclick="splitPDF()">✂️ Split PDF</button>
            </div>
            <div id="splitStatus"></div>
        </div>
    </div>

    <script>
        let currentPdfData = null;

        function updateFileList() {
            const files = document.getElementById('mergeFiles').files;
            const fileList = document.getElementById('fileList');
            const mergeBtn = document.getElementById('mergeBtn');
            
            if (files.length > 0) {
                let html = '<div class="file-info"><strong>Selected files:</strong><ul>';
                for (let file of files) {
                    html += `<li>${file.name}</li>`;
                }
                html += '</ul></div>';
                fileList.innerHTML = html;
                mergeBtn.disabled = files.length < 2;
            } else {
                fileList.innerHTML = '';
                mergeBtn.disabled = true;
            }
        }

        async function mergePDFs() {
            const files = document.getElementById('mergeFiles').files;
            const statusDiv = document.getElementById('mergeStatus');
            const btn = document.getElementById('mergeBtn');
            
            btn.disabled = true;
            showStatus(statusDiv, '🔄 Merging PDFs...', 'loading');

            try {
                const filesData = [];
                for (let file of files) {
                    const arrayBuffer = await file.arrayBuffer();
                    const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
                    filesData.push({
                        name: file.name,
                        data: base64
                    });
                }

                const response = await fetch('/api/merge', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        files: filesData
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, 'merged.pdf');
                    showStatus(statusDiv, '✅ PDFs merged successfully!', 'success');
                } else {
                    const error = await response.text();
                    showStatus(statusDiv, `❌ Error: ${error}`, 'error');
                }
            } catch (error) {
                showStatus(statusDiv, `❌ Error: ${error.message}`, 'error');
            } finally {
                btn.disabled = files.length < 2;
            }
        }

        async function analyzePDF() {
            const file = document.getElementById('splitFile').files[0];
            if (!file) return;

            try {
                const arrayBuffer = await file.arrayBuffer();
                const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        file: {
                            name: file.name,
                            data: base64
                        }
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('pageCount').textContent = `Total pages: ${result.pageCount}`;
                    document.getElementById('fileName').textContent = `File: ${file.name}`;
                    document.getElementById('pdfInfo').style.display = 'block';
                    currentPdfData = result;
                }
            } catch (error) {
                console.error('Error analyzing PDF:', error);
            }
        }

        async function splitPDF() {
            const pageInput = document.getElementById('pageNumbers').value.trim();
            const statusDiv = document.getElementById('splitStatus');
            
            const pages = parsePages(pageInput);
            showStatus(statusDiv, '✂️ Splitting PDF...', 'loading');

            try {
                const response = await fetch('/api/split', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        filename: currentPdfData.filename,
                        pages: pages
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, `split_pages_${pages.join('_')}.pdf`);
                    showStatus(statusDiv, '✅ PDF split successfully!', 'success');
                } else {
                    const error = await response.text();
                    showStatus(statusDiv, `❌ Error: ${error}`, 'error');
                }
            } catch (error) {
                showStatus(statusDiv, `❌ Error: ${error.message}`, 'error');
            }
        }

        function parsePages(input) {
            const pages = [];
            const parts = input.split(',');
            
            for (let part of parts) {
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
            }
            
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

        function showStatus(element, message, type) {
            element.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
    </script>
</body>
</html>'''

@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    """Handle PDF merge operation"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        if len(files) < 2:
            return jsonify({'error': 'At least 2 files required'}), 400
        
        pdf_writer = PdfWriter()
        
        for file_data in files:
            if not allowed_file(file_data['name']):
                return jsonify({'error': f"Invalid file: {file_data['name']}"}), 400
                
            file_bytes = base64.b64decode(file_data['data'])
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        return send_file(
            output, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name='merged.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_pdf():
    """Handle PDF analysis operation"""
    try:
        data = request.get_json()
        file_data = data.get('file')
        
        if not file_data or not allowed_file(file_data['name']):
            return jsonify({'error': 'Invalid file'}), 400
            
        file_bytes = base64.b64decode(file_data['data'])
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(pdf_reader.pages)
        
        filename = generate_filename(file_data['name'])
        pdf_cache[filename] = file_bytes
        
        return jsonify({
            'pageCount': page_count,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/split', methods=['POST'])
def split_pdf():
    """Handle PDF split operation"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        pages = data.get('pages')
        
        if filename not in pdf_cache:
            return jsonify({'error': 'PDF not found'}), 404
            
        file_bytes = pdf_cache[filename]
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(pdf_reader.pages)
        
        # Validate pages
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            return jsonify({'error': f'Invalid pages: {invalid_pages}'}), 400
        
        pdf_writer = PdfWriter()
        
        for page_num in sorted(pages):
            page_index = page_num - 1
            pdf_writer.add_page(pdf_reader.pages[page_index])
        
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        # Clean up
        del pdf_cache[filename]
        
        pages_str = '_'.join(map(str, sorted(pages)))
        return send_file(
            output, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name=f'split_pages_{pages_str}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# For development
if __name__ == '__main__':
    app.run(debug=True)

# Vercel handler - simple and clean!
handler = app