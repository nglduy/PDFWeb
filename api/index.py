# Simple Vercel Python handler for PDF operations
import json
import io
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import base64
import uuid
from urllib.parse import parse_qs

# Simple in-memory cache for this serverless function
pdf_cache = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def generate_filename(original_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}_{original_name}"

def get_html():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PDF Tools</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .section { background: #f8f9fa; padding: 25px; margin: 25px 0; border-radius: 10px; border-left: 5px solid #007bff; }
        .section h2 { color: #495057; margin-top: 0; }
        .btn { background: #007bff; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #0056b3; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        input[type="file"] { margin: 15px 0; padding: 10px; border: 2px dashed #dee2e6; border-radius: 5px; width: 100%; background: white; }
        input[type="text"] { padding: 10px; border: 1px solid #ced4da; border-radius: 5px; width: 100%; margin: 10px 0; }
        .status { margin: 15px 0; font-weight: bold; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .file-info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .loading { color: #007bff; }
        .upload-area { border: 2px dashed #007bff; padding: 20px; text-align: center; border-radius: 10px; background: #f8f9fa; margin: 15px 0; }
        .features { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }
        @media (max-width: 768px) { .features { grid-template-columns: 1fr; } }
        .feature-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 PDF Merger & Splitter</h1>
        <p style="text-align: center; color: #6c757d; margin-bottom: 30px;">Free online tool to merge multiple PDFs or split a PDF into individual pages</p>
        
        <div class="features">
            <div class="feature-box">
                <h3>📄 Merge PDFs</h3>
                <p>Combine multiple PDF files into one document</p>
            </div>
            <div class="feature-box">
                <h3>✂️ Split PDFs</h3>
                <p>Extract specific pages from a PDF file</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📄 Merge PDFs</h2>
            <div class="upload-area">
                <input type="file" id="mergeFiles" multiple accept=".pdf" onchange="updateFileList()">
            </div>
            <div id="fileList"></div>
            <button class="btn" id="mergeBtn" onclick="mergePDFs()" disabled>Merge PDFs</button>
            <div id="mergeStatus"></div>
        </div>
        
        <div class="section">
            <h2>✂️ Split PDF</h2>
            <div class="upload-area">
                <input type="file" id="splitFile" accept=".pdf" onchange="analyzePDF()">
            </div>
            <div id="pdfInfo" style="display:none;">
                <div class="file-info">
                    <p><strong>📊 PDF Information:</strong></p>
                    <p id="pageCount"></p>
                    <p id="fileName"></p>
                </div>
                <label for="pageNumbers"><strong>Pages to extract:</strong></label>
                <input type="text" id="pageNumbers" placeholder="Enter pages (e.g., 1,3,5-8 or 1-5,10-15)" />
                <p style="color: #6c757d; font-size: 14px;">💡 Examples: "1,3,5" for pages 1,3,5 | "1-5" for pages 1 through 5</p>
                <button class="btn" onclick="splitPDF()">Split PDF</button>
            </div>
            <div id="splitStatus"></div>
        </div>

        <div style="text-align: center; margin-top: 40px; color: #6c757d;">
            <p>🔒 Your files are processed securely and not stored on our servers</p>
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
                    html += `<li>${file.name} (${(file.size/1024/1024).toFixed(2)} MB)</li>`;
                }
                html += '</ul></div>';
                fileList.innerHTML = html;
                mergeBtn.disabled = files.length < 2;
                if (files.length < 2) {
                    fileList.innerHTML += '<p class="error">⚠️ Please select at least 2 PDF files to merge</p>';
                }
            } else {
                fileList.innerHTML = '';
                mergeBtn.disabled = true;
            }
        }

        async function mergePDFs() {
            const files = document.getElementById('mergeFiles').files;
            const statusDiv = document.getElementById('mergeStatus');
            const btn = document.getElementById('mergeBtn');
            
            if (files.length < 2) {
                showStatus(statusDiv, 'Please select at least 2 PDF files', 'error');
                return;
            }

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

                const response = await fetch('/api/index', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        action: 'merge',
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
                btn.disabled = false;
            }
        }

        async function analyzePDF() {
            const file = document.getElementById('splitFile').files[0];
            const statusDiv = document.getElementById('splitStatus');
            
            if (!file) return;

            showStatus(statusDiv, '🔍 Analyzing PDF...', 'loading');

            try {
                const arrayBuffer = await file.arrayBuffer();
                const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

                const response = await fetch('/api/index', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        action: 'analyze',
                        file: {
                            name: file.name,
                            data: base64
                        }
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    document.getElementById('pageCount').textContent = `📄 Total pages: ${result.pageCount}`;
                    document.getElementById('fileName').textContent = `📁 File: ${file.name}`;
                    document.getElementById('pdfInfo').style.display = 'block';
                    currentPdfData = result;
                    statusDiv.innerHTML = '';
                } else {
                    const error = await response.text();
                    showStatus(statusDiv, `❌ Error: ${error}`, 'error');
                }
            } catch (error) {
                showStatus(statusDiv, `❌ Error: ${error.message}`, 'error');
            }
        }

        async function splitPDF() {
            if (!currentPdfData) {
                alert('Please upload a PDF first');
                return;
            }

            const pageInput = document.getElementById('pageNumbers').value.trim();
            const statusDiv = document.getElementById('splitStatus');
            
            if (!pageInput) {
                showStatus(statusDiv, '⚠️ Please enter page numbers to extract', 'error');
                return;
            }

            const pages = parsePages(pageInput);
            if (pages.length === 0) {
                showStatus(statusDiv, '⚠️ Please enter valid page numbers', 'error');
                return;
            }

            showStatus(statusDiv, '✂️ Splitting PDF...', 'loading');

            try {
                const response = await fetch('/api/index', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        action: 'split',
                        filename: currentPdfData.filename,
                        pages: pages
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    downloadFile(blob, `split_pages_${pages.join('_')}.pdf`);
                    showStatus(statusDiv, `✅ PDF split successfully! Extracted pages: ${pages.join(', ')}`, 'success');
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
                    if (!isNaN(start) && !isNaN(end) && start <= end) {
                        for (let i = start; i <= end; i++) {
                            pages.push(i);
                        }
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

        document.getElementById('mergeFiles').addEventListener('change', updateFileList);
    </script>
</body>
</html>'''

def handle_merge(files):
    """Handle PDF merge operation"""
    if len(files) < 2:
        raise ValueError("At least 2 files required")
    
    pdf_writer = PdfWriter()
    
    for file_data in files:
        if not allowed_file(file_data['name']):
            raise ValueError(f"Invalid file: {file_data['name']}")
            
        file_bytes = base64.b64decode(file_data['data'])
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
    
    output = io.BytesIO()
    pdf_writer.write(output)
    
    return output.getvalue()

def handle_analyze(file_data):
    """Handle PDF analysis operation"""
    if not file_data or not allowed_file(file_data['name']):
        raise ValueError("Invalid file")
        
    file_bytes = base64.b64decode(file_data['data'])
    pdf_reader = PdfReader(io.BytesIO(file_bytes))
    page_count = len(pdf_reader.pages)
    
    filename = generate_filename(file_data['name'])
    pdf_cache[filename] = file_bytes
    
    return {
        'pageCount': page_count,
        'filename': filename
    }

def handle_split(filename, pages):
    """Handle PDF split operation"""
    if filename not in pdf_cache:
        raise ValueError("PDF not found")
        
    file_bytes = pdf_cache[filename]
    pdf_reader = PdfReader(io.BytesIO(file_bytes))
    total_pages = len(pdf_reader.pages)
    
    # Validate pages
    invalid_pages = [p for p in pages if p < 1 or p > total_pages]
    if invalid_pages:
        raise ValueError(f"Invalid pages: {invalid_pages}")
    
    pdf_writer = PdfWriter()
    
    for page_num in sorted(pages):
        page_index = page_num - 1
        pdf_writer.add_page(pdf_reader.pages[page_index])
    
    output = io.BytesIO()
    pdf_writer.write(output)
    
    # Clean up
    del pdf_cache[filename]
    
    return output.getvalue()

def handler(request):
    """Vercel serverless function handler"""
    try:
        # CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        
        # Handle OPTIONS (preflight) request
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Handle GET request - serve HTML
        if request.method == 'GET':
            return {
                'statusCode': 200,
                'headers': {
                    **headers,
                    'Content-Type': 'text/html',
                },
                'body': get_html()
            }
        
        # Handle POST request - process PDFs
        if request.method == 'POST':
            # Parse request body
            body = json.loads(request.body)
            action = body.get('action')
            
            if action == 'merge':
                result = handle_merge(body.get('files', []))
                return {
                    'statusCode': 200,
                    'headers': {
                        **headers,
                        'Content-Type': 'application/pdf',
                        'Content-Disposition': 'attachment; filename="merged.pdf"'
                    },
                    'body': base64.b64encode(result).decode(),
                    'isBase64Encoded': True
                }
                
            elif action == 'analyze':
                result = handle_analyze(body.get('file'))
                return {
                    'statusCode': 200,
                    'headers': {
                        **headers,
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps(result)
                }
                
            elif action == 'split':
                result = handle_split(body.get('filename'), body.get('pages'))
                pages_str = '_'.join(map(str, sorted(body.get('pages'))))
                return {
                    'statusCode': 200,
                    'headers': {
                        **headers,
                        'Content-Type': 'application/pdf',
                        'Content-Disposition': f'attachment; filename="split_pages_{pages_str}.pdf"'
                    },
                    'body': base64.b64encode(result).decode(),
                    'isBase64Encoded': True
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid action'})
                }
        
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'error': f'Server error: {str(e)}'})
        }